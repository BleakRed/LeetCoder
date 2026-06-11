#!/usr/bin/env python3
"""LeetCoder — automatically fetch, scaffold, and submit LeetCode daily challenges."""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from string import Template

CONFIG_DIR = Path.home() / ".config" / "leetd"
CONFIG_FILE = CONFIG_DIR / "config.json"
REPO_DIR = Path(__file__).resolve().parent
SOLUTIONS_DIR = REPO_DIR / "solutions"
LANGS_DIR = {lang: SOLUTIONS_DIR / lang for lang in
             ["python", "javascript", "typescript", "java", "cpp", "go", "rust", "csharp"]}

DEFAULT_LANG = "python"
LEETCODE_GRAPHQL = "https://leetcode.com/graphql"

DAILY_QUERY = """
query questionOfToday {
  activeDailyCodingChallengeQuestion {
    date
    link
    question {
      questionId
      title
      titleSlug
      difficulty
      topicTags { name slug }
      similarQuestions
      exampleTestcases
      codeSnippets { lang langSlug code }
    }
  }
}
"""

PROBLEM_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    title
    titleSlug
    difficulty
    content
    topicTags { name slug }
    hints
    exampleTestcases
    codeSnippets { lang langSlug code }
  }
}
"""

BOILERPLATES = {
    "python": Template("""$code


def run_tests():
    solution = Solution()
    test_cases = []
    expected = []

    for i, (args, exp) in enumerate(zip(test_cases, expected)):
        result = solution$call
        status = "PASS" if result == exp else "FAIL"
        print(f"Test {i}: {status} (got {result}, expected {exp})")


if __name__ == "__main__":
    run_tests()
"""),
    "javascript": Template("""$code


// Add your test cases here
const testCases = [];
const expected = [];

for (let i = 0; i < testCases.length; i++) {
    const result = $call;
    const status = JSON.stringify(result) === JSON.stringify(expected[i]) ? "PASS" : "FAIL";
    console.log(`Test $${i}: $${status} (got $${JSON.stringify(result)}, expected $${JSON.stringify(expected[i])})`);
}
"""),
    "typescript": Template("""$code


// Add your test cases here
const testCases: any[] = [];
const expected: any[] = [];

for (let i = 0; i < testCases.length; i++) {
    const result = $call;
    const status = JSON.stringify(result) === JSON.stringify(expected[i]) ? "PASS" : "FAIL";
    console.log(`Test $${i}: $${status} (got $${JSON.stringify(result)}, expected $${JSON.stringify(expected[i])})`);
}
"""),
    "java": Template("""$code

    public static void main(String[] args) {
        Solution sol = new Solution();
        // Add test cases here
    }
}
"""),
    "cpp": Template("""$code
"""),
}

CALL_SIGNATURES = {
    "python": ("solution.$method($args)", "solution = Solution()\n    "),
    "javascript": ("solution.$method($args)", "const solution = new Solution();\n    "),
    "typescript": ("solution.$method($args)", "const solution = new Solution();\n    "),
    "java": ("sol.$method($args)", "Solution sol = new Solution();\n        "),
    "cpp": ("sol.$method($args)", "Solution sol;\n    "),
}


def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def graphql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    req = urllib.request.Request(
        LEETCODE_GRAPHQL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "leetd/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP error: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def fetch_daily():
    data = graphql(DAILY_QUERY)
    q = data["data"]["activeDailyCodingChallengeQuestion"]
    return {
        "date": q["date"],
        "title": q["question"]["title"],
        "titleSlug": q["question"]["titleSlug"],
        "difficulty": q["question"]["difficulty"],
        "questionId": q["question"]["questionId"],
        "link": "https://leetcode.com" + q["link"],
        "snippets": q["question"]["codeSnippets"],
        "topicTags": [t["name"] for t in q["question"]["topicTags"]],
    }


def fetch_problem(title_slug):
    data = graphql(PROBLEM_QUERY, {"titleSlug": title_slug})
    q = data["data"]["question"]
    return {
        "title": q["title"],
        "titleSlug": q["titleSlug"],
        "difficulty": q["difficulty"],
        "questionId": q["questionId"],
        "content": q["content"],
        "hints": q.get("hints", []),
        "snippets": q["codeSnippets"],
        "topicTags": [t["name"] for t in q["topicTags"]],
    }


LEETCODE_API = "https://leetcode.com/api/problems/all/"


def fetch_problem_list():
    """Fetch all problems and return {questionId: titleSlug} mapping."""
    req = urllib.request.Request(LEETCODE_API, headers={"User-Agent": "leetd/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP error: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    problems = {}
    for pair in data.get("stat_status_pairs", []):
        stat = pair.get("stat", {})
        qid = stat.get("frontend_question_id")
        slug = stat.get("question__title_slug")
        if qid is not None and slug:
            problems[qid] = slug
    return problems


def find_slug_by_id(problem_id):
    """Find a problem's titleSlug by its numeric frontend ID."""
    problems = fetch_problem_list()
    slug = problems.get(problem_id)
    if not slug:
        print(f"Problem #{problem_id} not found.", file=sys.stderr)
        sys.exit(1)
    return slug


def get_lang_slug(lang):
    mapping = {
        "py": "python", "python": "python",
        "js": "javascript", "javascript": "javascript",
        "ts": "typescript", "typescript": "typescript",
        "java": "java",
        "cpp": "cpp", "c++": "cpp",
        "go": "golang",
        "rs": "rust", "rust": "rust",
        "cs": "csharp", "csharp": "csharp",
    }
    return mapping.get(lang.lower(), lang.lower())


def find_snippet(snippets, lang_slug):
    if not snippets:
        return None
    for s in snippets:
        if s["langSlug"] == lang_slug:
            return s["code"]
    return None


def detect_method(code):
    match = re.search(r"def (\w+)\((.*?)\)", code, re.DOTALL)
    if match:
        method = match.group(1)
        params = match.group(2).strip()
        params = re.sub(r'\bself\b\s*[,]*\s*', '', params).strip()
        return method, params
    return "unknown", ""


def detect_method_js(code):
    match = re.search(r"(?:function\s+)?(\w+)\s*[=(]\s*(?:function\s*)?\(", code)
    if not match:
        match = re.search(r"var\s+(\w+)\s*=\s*(?:function|\(.*\)\s*=>)", code)
    return (match.group(1), "") if match else ("unknown", "")


def scaffold_code(lang_slug, code):
    if lang_slug not in BOILERPLATES:
        return code

    if lang_slug == "python":
        method, params = detect_method(code)
        method = method or "unknown"
        if params:
            param_names = [p.split("=")[0].strip().split()[-1] for p in params.split(",") if p.strip() and not p.strip().startswith("*")]
            args = ", ".join(param_names)
        else:
            args = ""
        call_sig = f".{method}({args})"
        return BOILERPLATES[lang_slug].safe_substitute(code=code, call=call_sig, method=method)
    elif lang_slug in ("javascript", "typescript"):
        method, _ = detect_method_js(code)
        method = method or "unknown"
        call_sig = f"solution.{method}()"
        return BOILERPLATES[lang_slug].safe_substitute(code=code, call=call_sig, method=method)
    elif lang_slug in ("java", "cpp"):
        return BOILERPLATES[lang_slug].safe_substitute(code=code)

    return code


def file_ext(lang_slug):
    ext_map = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "java": ".java",
        "cpp": ".cpp",
        "golang": ".go",
        "rust": ".rs",
        "csharp": ".cs",
    }
    return ext_map.get(lang_slug, ".txt")


def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name.replace(' ', '_')).lower()


def cmd_fetch(args):
    lang = get_lang_slug(args.lang or load_config().get("lang", DEFAULT_LANG))

    if args.problem_id is not None:
        slug = find_slug_by_id(args.problem_id)
        problem = fetch_problem(slug)
        qid = problem["questionId"]
        title = problem["title"]
        slug = problem["titleSlug"]
        difficulty = problem["difficulty"]
        snippets = problem["snippets"]
        topic_tags = problem["topicTags"]
        link = f"https://leetcode.com/problems/{slug}/"
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    else:
        daily = fetch_daily()
        qid = daily["questionId"]
        title = daily["title"]
        slug = daily["titleSlug"]
        difficulty = daily["difficulty"]
        snippets = daily["snippets"]
        topic_tags = daily["topicTags"]
        link = daily["link"]
        date_str = daily["date"]

    code = find_snippet(snippets, lang)

    if not code:
        print(f"No snippet found for language '{lang}'. Available:", file=sys.stderr)
        for s in snippets or []:
            print(f"  - {s['lang']} ({s['langSlug']})", file=sys.stderr)
        sys.exit(1)

    dir = LANGS_DIR.get(lang)
    if not dir:
        print(f"Unsupported language: {lang}", file=sys.stderr)
        sys.exit(1)
    dir.mkdir(parents=True, exist_ok=True)

    ext = file_ext(lang)
    if args.problem_id is not None:
        filename = f"{int(qid):04d}_{sanitize_filename(title)}{ext}"
    else:
        filename = f"{date_str}_{sanitize_filename(title)}{ext}"
    filepath = dir / filename

    code = scaffold_code(lang, code)

    header = (
        f"# {title}\n"
        f"# Difficulty: {difficulty}\n"
        f"# Date: {date_str}\n"
        f"# Link: {link}\n"
        f"# Tags: {', '.join(topic_tags)}\n\n"
    )
    if lang in ("javascript", "typescript"):
        header = "// " + header.replace("\n", "\n// ").rstrip("// ") + "\n"
    elif lang == "java":
        header = "// " + header.replace("\n", "\n// ").rstrip("// ") + "\n"
    elif lang == "cpp":
        header = "// " + header.replace("\n", "\n// ").rstrip("// ") + "\n"

    content = header + code
    filepath.write_text(content)
    print(f"Created {filepath}")

    if args.open:
        editor = args.editor or load_config().get("editor") or os.environ.get("EDITOR", "vim")
        subprocess.run([editor, str(filepath)])


def cmd_show(args):
    if args.number is not None:
        slug = find_slug_by_id(args.number)
    elif args.slug:
        slug = args.slug
    else:
        daily = fetch_daily()
        slug = daily["titleSlug"]
    problem = fetch_problem(slug)

    print(f"\n{'='*60}")
    print(f"  {problem['questionId']}. {problem['title']}")
    print(f"  Difficulty: {problem['difficulty']}")
    print(f"  Tags: {', '.join(problem['topicTags'])}")
    print(f"  https://leetcode.com/problems/{slug}/")
    print(f"{'='*60}\n")

    if problem.get("content"):
        import html
        text = re.sub(r'<[^>]+>', '', problem["content"])
        text = html.unescape(text)
        print(text[:2000] + ("..." if len(text) > 2000 else ""))
        print()

    if problem.get("hints"):
        print("HINTS:")
        for i, h in enumerate(problem["hints"], 1):
            import html
            hint_text = re.sub(r'<[^>]+>', '', h)
            hint_text = html.unescape(hint_text)
            print(f"  {i}. {hint_text[:300]}")

    lang = get_lang_slug(args.lang or load_config().get("lang", DEFAULT_LANG))
    snippets = problem["snippets"]
    code = find_snippet(snippets, lang)
    if code:
        print(f"\n--- Starter Code ({lang}) ---\n")
        print(code)


def cmd_submit(args):
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    slug = args.slug
    if not slug:
        m = re.search(r'\d{4}-\d{2}-\d{2}_(.+)', filepath.stem)
        if m:
            slug = m.group(1)
        else:
            print("Could not determine slug. Provide --slug.", file=sys.stderr)
            sys.exit(1)

    code = filepath.read_text()
    if args.lang:
        lang_slug = get_lang_slug(args.lang)
    else:
        ext = filepath.suffix
        ext_map = {".py": "python", ".js": "javascript", ".ts": "typescript",
                    ".java": "java", ".cpp": "cpp", ".go": "golang",
                    ".rs": "rust", ".cs": "csharp"}
        lang_slug = ext_map.get(ext, "python")

    print(f"Submitting {filepath.name} for problem '{slug}' ({lang_slug})...")
    print("This requires a browser with Playwright. Installing if needed...")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Installing playwright...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright", "-q"], check=True)
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"], check=True)
        from playwright.sync_api import sync_playwright

    config = load_config()
    leet_username = args.username or config.get("leetcode_username") or input("LeetCode username/email: ")
    leet_password = args.password or config.get("leetcode_password") or input("LeetCode password: ")

    if args.save_credentials:
        config["leetcode_username"] = leet_username
        config["leetcode_password"] = leet_password
        save_config(config)

    submit_url = f"https://leetcode.com/problems/{slug}/submit/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.visible)
        ctx = browser.new_context()
        page = ctx.new_page()

        print("Logging into LeetCode...")
        page.goto("https://leetcode.com/accounts/login/")
        page.wait_for_selector('input[name="login"]', timeout=20000)
        page.fill('input[name="login"]', leet_username)
        page.fill('input[name="password"]', leet_password)
        page.click('button[type="submit"]')
        page.wait_for_url("https://leetcode.com/**", timeout=30000)
        print("Logged in!")

        print("Navigating to submission page...")
        page.goto(submit_url)
        page.wait_for_timeout(3000)

        try:
            page.wait_for_selector('[class*="editor"]', timeout=15000)
            editor = page.locator('[class*="editor"]').first
            editor.click()
            page.keyboard.select_all()
            page.keyboard.press("Backspace")
            page.keyboard.type(code, delay=10)
            page.wait_for_timeout(500)
        except Exception as e:
            print(f"Editor interaction failed: {e}", file=sys.stderr)

        submit_btn = page.locator('button:has-text("Submit")')
        if submit_btn.count() == 0:
            submit_btn = page.locator('[data-cy="submit-code-btn"]')
        if submit_btn.count() == 0:
            submit_btn = page.locator('button:has-text("Sub")')

        if submit_btn.count() > 0:
            submit_btn.first.click()
            print("Submitted! Waiting for results...")
            page.wait_for_timeout(15000)
            ctx.storage_state(path=str(CONFIG_DIR / "auth.json"))
            print("Check the browser for results." if args.visible else "Session saved.")
        else:
            print("Could not find submit button.", file=sys.stderr)

        if not args.visible:
            browser.close()


def cmd_config(args):
    config = load_config()
    if args.set and args.value:
        config[args.set] = args.value
        save_config(config)
        print(f"Set {args.set} = {args.value}")
    elif args.get:
        print(config.get(args.get, ""))
    else:
        print(json.dumps(config, indent=2))
        print(f"\nConfig file: {CONFIG_FILE}")


def cmd_solve(args):
    import html
    lang = get_lang_slug(args.lang or load_config().get("lang", DEFAULT_LANG))

    if args.problem_id is not None:
        slug = find_slug_by_id(args.problem_id)
    else:
        daily = fetch_daily()
        slug = daily["titleSlug"]

    problem = fetch_problem(slug)
    snippets = problem["snippets"]
    starter_code = find_snippet(snippets, lang) or ""

    text = re.sub(r'<[^>]+>', '', problem.get("content", ""))
    text = html.unescape(text)

    prompt = f"""You are solving a LeetCode problem. Write a solution in {lang}.

Problem: {problem['questionId']}. {problem['title']}
Difficulty: {problem['difficulty']}
Tags: {', '.join(problem['topicTags'])}
URL: https://leetcode.com/problems/{slug}/

Description:
{text.strip()}

"""
    if problem.get("hints"):
        prompt += "Hints:\n"
        for i, h in enumerate(problem["hints"], 1):
            hint_text = html.unescape(re.sub(r'<[^>]+>', '', h))
            prompt += f"  {i}. {hint_text}\n"
        prompt += "\n"

    if starter_code:
        prompt += f"Starter code ({lang}):\n```{lang}\n{starter_code}\n```\n\n"

    prompt += f"""Write only the solution code in {lang}. Output the code inside a code block.
The code must pass all LeetCode test cases efficiently.
Include the class/function definition exactly as in the starter code."""

    if args.output:
        args.output.write_text(prompt)
        print(f"Prompt written to {args.output}")
    else:
        print(prompt)


def cmd_list(args):
    lang = get_lang_slug(args.lang) if args.lang else None
    targets = [LANGS_DIR[lang]] if lang else LANGS_DIR.values()
    found = []
    for d in targets:
        if d.exists():
            for f in sorted(d.iterdir(), reverse=True):
                found.append((d.name, f.name, f))
    for lang_name, fname, fpath in found[:20]:
        print(f"  [{lang_name}] {fname}")
    if not found:
        print("No solutions yet. Run 'leetd fetch' to get started.")


def main():
    parser = argparse.ArgumentParser(
        prog="leetd",
        description="LeetCoder — LeetCode daily challenge automation.",
    )
    sub = parser.add_subparsers(dest="command")

    p_fetch = sub.add_parser("fetch", help="Fetch a problem and create solution file")
    p_fetch.add_argument("problem_id", nargs="?", type=int, help="Problem number (default: daily challenge)")
    p_fetch.add_argument("-l", "--lang", help="Programming language")
    p_fetch.add_argument("-o", "--open", action="store_true", help="Open in editor after creation")
    p_fetch.add_argument("-e", "--editor", help="Editor to use (default: $EDITOR)")
    p_fetch.set_defaults(func=cmd_fetch)

    p_show = sub.add_parser("show", help="Display problem info")
    p_show.add_argument("slug", nargs="?", help="Problem slug (default: daily)")
    p_show.add_argument("-n", "--number", type=int, help="Problem number")
    p_show.add_argument("-l", "--lang", help="Language for starter code")
    p_show.set_defaults(func=cmd_show)

    p_submit = sub.add_parser("submit", help="Submit solution to LeetCode")
    p_submit.add_argument("file", help="Path to solution file")
    p_submit.add_argument("-s", "--slug", help="Problem slug (auto-detected from filename)")
    p_submit.add_argument("-l", "--lang", help="Language (auto-detected from extension)")
    p_submit.add_argument("-u", "--username", help="LeetCode username/email")
    p_submit.add_argument("-p", "--password", help="LeetCode password")
    p_submit.add_argument("--visible", action="store_true", help="Show browser (not headless)")
    p_submit.add_argument("--save-credentials", action="store_true", help="Save credentials to config")
    p_submit.set_defaults(func=cmd_submit)

    p_solve = sub.add_parser("solve", help="Generate a prompt for an LLM to solve a problem")
    p_solve.add_argument("problem_id", nargs="?", type=int, help="Problem number (default: daily challenge)")
    p_solve.add_argument("-l", "--lang", help="Programming language")
    p_solve.add_argument("-o", "--output", type=Path, help="Write prompt to file instead of stdout")
    p_solve.set_defaults(func=cmd_solve)

    p_config = sub.add_parser("config", help="Get/set configuration")
    p_config.add_argument("--set", metavar="KEY", help="Config key to set")
    p_config.add_argument("--value", metavar="VAL", help="Config value")
    p_config.add_argument("--get", metavar="KEY", help="Get config value")
    p_config.set_defaults(func=cmd_config)

    p_list = sub.add_parser("list", help="List saved solutions")
    p_list.add_argument("-l", "--lang", help="Filter by language")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
    for d in LANGS_DIR.values():
        d.mkdir(parents=True, exist_ok=True)

    args.func(args)


if __name__ == "__main__":
    main()
