import re

def check_file(path):
    with open(path, 'r') as f:
        content = f.read()
    
    # Check for "arrow" not preceded by backslash
    arrows = re.finditer(r'(?<!\\)arrow', content)
    print("--- 'arrow' occurrences (potential typos) ---")
    for m in arrows:
        start = max(0, m.start() - 20)
        end = min(len(content), m.end() + 20)
        print(f"Line {content[:m.start()].count(chr(10)) + 1}: ...{content[start:end]}...")

    # Check for mismatched delimiters
    print("\n--- Mismatched Delimiters ---")
    math_blocks = re.finditer(r'\$\$(.+?)\$\$', content, re.DOTALL)
    for m in math_blocks:
        block = m.group(1)
        lefts = block.count(r'\left')
        rights = block.count(r'\right')
        if lefts != rights:
            print(f"Line {content[:m.start()].count(chr(10)) + 1}: Mismatch! \\left={lefts}, \\right={rights}")
            print(f"Block: {block[:100]}...")

    # Check for image descriptions
    print("\n--- Image Descriptions ---")
    imgs = re.finditer(r'!\[(.*?)\]\((.*?)\)', content)
    for m in imgs:
        alt = m.group(1)
        url = m.group(2)
        if len(alt) > 50 or not url:
            print(f"Line {content[:m.start()].count(chr(10)) + 1}: Potential description")
            print(f"Alt: {alt[:50]}...")
            print(f"URL: {url}")

check_file('datalab_output_3/1749-000-022-008.md')
