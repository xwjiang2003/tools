# -*- coding: utf-8 -*-
"""English copy for the site."""

SITE_EN = {
    'title': 'DevTools — Free Online Developer Tools That Run in Your Browser',
    'description': (
        'A free collection of browser-based developer tools: JSON formatting and validation, '
        'text diffing, encoding, regex testing, timestamps, hashing, code formatting and generators.'
    ),
    'keywords': (
        'online developer tools,json formatter,text diff,base64 encode,regex tester,'
        'unix timestamp,hash generator,code formatter,uuid generator'
    ),
}

TOOLS_EN = {
    'json': {
        'nav': 'JSON',
        'title': 'JSON Formatter & Validator — Free, In-Browser | DevTools',
        'description': (
            'Format, validate, minify and sort JSON, convert between JSON and CSV, XML or YAML, '
            'diff two documents and query with JSONPath — all locally in your browser.'
        ),
        'keywords': (
            'JSON formatter,JSON validator,JSON beautifier,JSON minify,JSON sort,JSON escape,'
            'JSON tree view,JSON diff,JSON to CSV,JSON to XML,JSON to YAML,JSONPath tester'
        ),
        'h1': 'JSON Formatter, Validator & Converter',
        'intro': [
            'A browser-only JSON toolbox that keeps the everyday jobs in one place: format, minify, '
            'validate, sort, escape and tree view, plus diffing, format conversion and JSONPath queries.',
            'Every parse and conversion happens inside your browser, so the JSON itself never reaches a '
            'server. If you spend your day pasting API responses, config files and log fragments, that '
            'matters more than any single feature.',
        ],
        'features': [
            ('Format & Minify',
             'Pretty-print with 2-space, 4-space or tab indentation, or collapse to a single line and '
             'see the before/after size and compression ratio.'),
            ('Validation',
             'Parse errors come back with a message and the exact position, plus a structural overview, '
             'so a missing quote or stray comma is easy to find.'),
            ('Recursive Sort',
             'Sort the whole object tree alphabetically by key, ascending or descending — handy when '
             'comparing two config files.'),
            ('Escape & Unescape',
             'Character-by-character escaping and unescaping of JSON strings, avoiding the edge cases '
             'that regex-based replacement runs into.'),
            ('Tree View',
             'A collapsible tree that labels the type of every node, with one-click expand and collapse all.'),
            ('JSON Diff',
             'Line-level comparison of two JSON documents; turn on semantic mode to ignore differences '
             'caused purely by key order.'),
            ('Format Conversion',
             'Two-way conversion between JSON and CSV, XML and YAML, with a button to swap the direction.'),
            ('JSONPath Queries',
             'Supports $.key, [*], the recursive .. operator, filters such as [?(@.price>100)], '
             'array slices and multi-index selectors.'),
        ],
        'steps': [
            'Paste or type your JSON in the editor on the left, or click "Sample" to load demo data.',
            'Pick a tab on the right: Basic, Diff, Convert or JSONPath.',
            'Under Basic, click Format, Minify or Validate; the output appears in the result panel below.',
            'Diff and Convert need two inputs — fill in both sides as prompted, then run.',
        ],
        'faq': [
            ('Is my JSON uploaded anywhere?',
             'No. Parsing, formatting, diffing and conversion are all done by JavaScript in your browser, '
             'and the page contains no code that sends JSON to a backend. You can keep using these features '
             'offline once the editor dependency has loaded.'),
            ('Validation fails, but the JSON looks fine. Why?',
             'The four usual suspects are a trailing comma after the last item of an object or array, '
             'single quotes instead of double quotes, a literal newline inside a string that was never '
             'escaped, and an invisible BOM at the start of the file. The error message includes the '
             'position, so moving the cursor there usually reveals the problem.'),
            ('How is JSON different from a JavaScript object literal?',
             'JSON requires double-quoted keys, forbids trailing commas and comments, and has no '
             'undefined, functions or single-quoted strings. Object literals allow all of those, which is '
             'why copying an object straight out of JavaScript source often fails validation.'),
            ('How large a JSON document can it handle?',
             'That depends on the memory your browser has available; a few tens of megabytes is normally '
             'fine. For hundreds of megabytes, reach for a command-line tool such as jq — the browser '
             'editor gets noticeably sluggish at that size.'),
        ],
    },
    'diff': {
        'nav': 'Text Diff',
        'title': 'Text Diff Checker — Compare Code & Text Online | DevTools',
        'description': (
            'Paste two texts or files and see added, removed and changed lines highlighted instantly, '
            'in unified or side-by-side view. Nothing leaves your browser.'
        ),
        'keywords': (
            'text diff,text compare,online diff,diff checker,compare two texts,code diff,'
            'string compare,side by side diff'
        ),
        'h1': 'Online Text Diff Checker',
        'intro': [
            'Paste the two versions into the left and right panes and the page computes a line-level diff '
            'as you type, colour-coding added, removed and modified content. It suits two configs, two '
            'revisions of a file, two log excerpts, or a change someone sent you.',
            'The comparison runs entirely in your browser; the text is never uploaded.',
        ],
        'features': [
            ('Unified View',
             'Shows differences line by line with + and - prefixes, close to the git diff reading '
             'experience.'),
            ('Side-by-Side',
             'Two aligned columns with changed lines matched up, which makes checking line by line much easier.'),
            ('Case Sensitivity',
             'Turn case sensitivity off to ignore the difference between Hello and hello.'),
            ('Ignore Whitespace',
             'Ignore leading and trailing spaces and indentation changes, and focus on the content itself.'),
            ('Live Comparison',
             'The diff recalculates as you type — there is no button to press.'),
        ],
        'steps': [
            'Paste the original text into "Original text A" on the left.',
            'Paste the updated text into "Compared text B" on the right.',
            'Choose unified view or side-by-side view above.',
            'Toggle "Case sensitive" and "Ignore whitespace" to suit the comparison.',
        ],
        'faq': [
            ('What do the colours in the result mean?',
             'A green background marks added lines, a red background marks removed ones, and uncoloured '
             'lines are identical on both sides. Changed words within a line are highlighted more strongly '
             'so you can find them inside long lines.'),
            ('Can it compare binary files?',
             'No. This is a line-level text comparison; binary data needs a dedicated hexadecimal diff tool.'),
            ('Will very large texts be slow?',
             'The algorithm scales with the number of lines, and anything up to a few thousand lines is '
             'effectively instant. With tens of thousands of lines and very large differences the browser '
             'may briefly stutter, so it is worth trimming to the section you actually need to check.'),
            ('Are the two texts I compare saved or uploaded?',
             'No. The comparison runs entirely in your browser; the page contains no code that sends your text anywhere and writes no logs. It keeps working offline (the first load needs the network for page resources).'),
        ],
        'seealso': [
            ('Text case & style converter', 'string/'),
            ('Regex tester', 'regex/'),
            ('Case converter (camel/snake/kebab)', 'case/'),
            ('JSON formatter & validator', './'),
        ],

    },
    'encode': {
        'nav': 'Encode',
        'title': 'Base64 / URL / Unicode Encoder & Decoder Online | DevTools',
        'description': (
            'Encode and decode Base64, URL percent-encoding, Unicode escapes, HTML entities and hex, '
            'with correct UTF-8 handling. Runs locally in your browser.'
        ),
        'keywords': (
            'base64 encode,base64 decode,base64 online,url encode,url decode,unicode converter,'
            'html entity escape,hex encode,hex to text'
        ),
        'h1': 'Base64 / URL / Unicode Encoder & Decoder',
        'intro': [
            'One page for the encodings you reach for most often: Base64, URL percent-encoding, Unicode '
            'escapes, HTML entities and hexadecimal. Choose the format, click Encode or Decode, and the '
            'result appears below — multi-byte characters included, with no mangled text.',
            'Every conversion happens locally, so the text you paste never leaves your device.',
        ],
        'features': [
            ('Base64',
             'Convert text to and from Base64 with proper UTF-8 handling, and turn image files into '
             'Base64 data URLs.'),
            ('URL Encoding',
             'encodeURIComponent and decodeURIComponent, the right choice for query parameter values and '
             'path segments.'),
            ('Unicode',
             'Convert between \\uXXXX escape sequences and readable text, for a whole document at once.'),
            ('HTML Entities',
             'Convert to and from &lt;, &amp;, &#xXXXX; and friends when you need to display source code '
             'or defuse markup.'),
            ('Hex',
             'Convert strings to hexadecimal byte sequences and back.'),
        ],
        'steps': [
            'Enter the text you want to process on the left.',
            'Pick Base64, URL, Unicode, HTML entities or Hex on the right.',
            'Click Encode or Decode; the result shows up in the panel below.',
            'Use the Copy button on the result panel to take it with you.',
        ],
        'faq': [
            ('Is Base64 encryption?',
             'No. Base64 is only a way of representing binary data with printable characters, and anyone '
             'can reverse it directly. It provides no confidentiality whatsoever; when secrecy matters, '
             'use a real cipher such as AES.'),
            ('Why does a Base64 string end with equals signs?',
             'The equals signs are padding. Base64 encodes every 3 bytes as 4 characters, so when the '
             'input length is not a multiple of 3, one or two = characters are appended to keep the output '
             'length a multiple of 4.'),
            ('Should I use encodeURI or encodeURIComponent?',
             'Use encodeURIComponent for individual query parameter values, because it also escapes '
             '&, =, ? and /. Use encodeURI when escaping a whole URL that must keep its structure, since '
             'it leaves those syntactic characters alone.'),
            ('The decoded text is garbled. What went wrong?',
             'Usually the original was encoded with a character set other than UTF-8, or the content was '
             'encoded twice. Try decoding once more and see whether the result still looks encoded; this '
             'page always treats text as UTF-8.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Hex to Decimal / Binary', 'hex/'),
            ('Any-Base Converter', 'base/'),
            ('Is the content I encode uploaded?',
             'No. Base64, URL, Unicode, HTML entity and hex encoding/decoding all run in JavaScript in your browser. Your input never leaves the device and the tool works offline.'),
        ],
    },
    'regex': {
        'nav': 'Regex',
        'title': 'Regex Tester Online — Live Highlight & Replace | DevTools',
        'description': (
            'Test regular expressions with live match highlighting, g/i/m/s/u flags, capture group '
            'details and a replacement preview, plus common patterns. Runs locally.'
        ),
        'keywords': (
            'regex tester,regex online,regular expression tester,regex match,regex replace,'
            'regex syntax,common regex patterns'
        ),
        'h1': 'Regex Tester & Replacement Preview',
        'intro': [
            'Write the pattern and watch the matches appear: enter your expression and flags at the top, '
            'put the test text on the left, and see every match highlighted on the right along with its '
            'position and capture groups.',
            'Below that you can preview a replacement using $1 and $2 backreferences, so you can iterate '
            'without switching tools.',
        ],
        'features': [
            ('Live Highlighting',
             'Matches are computed as you type and every hit is marked directly in the test text.'),
            ('Flag Toggles',
             'g for global, i for case-insensitive, m for multiline, s for dot-matches-newline and '
             'u for Unicode, each switched independently.'),
            ('Match Details',
             'Every match lists its text, start position and the value captured by each group.'),
            ('Replace Preview',
             'Enter a replacement template and see the result immediately, with $1, $& and the rest of '
             'the substitution syntax.'),
            ('Common Patterns',
             'Ready-made expressions for email addresses, phone numbers and URLs that you can drop in '
             'and adjust.'),
        ],
        'steps': [
            'Type the expression into the regex field and tick the g / i / m / s / u flags as needed.',
            'Paste the content to search into "Test text" on the left.',
            'Review the highlights and capture group details under "Matches" on the right.',
            'Switch to replace mode, enter a replacement template and check the preview.',
        ],
        'faq': [
            ('Which regex engine does this use?',
             'The browser native JavaScript RegExp engine, following ECMAScript syntax. It is broadly '
             'compatible with Python, PCRE and Java, but features such as (?P<name>...) named groups and '
             'variable-length lookbehind differ, so keep that in mind when moving a pattern between languages.'),
            ('Why does my pattern match nothing?',
             'Three common causes: the g flag is off, so only the first occurrence can be found; special '
             'characters are unescaped — matching a literal dot requires \\.; or m and s are unchecked, so '
             '^, $ and . behave differently from what you expect.'),
            ('What is the difference between greedy and lazy matching?',
             'The quantifiers * and + are greedy by default and consume as much as possible. Appending a '
             'question mark makes them lazy (*? or +?), consuming as little as possible. Against <a><b>, '
             'the pattern <.+> matches the whole string while <.+?> matches only <a>.'),
            ('Does the page record the patterns and text I enter?',
             'No. Matching and replacement both run inside your browser, and your input is never sent to '
             'a server.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Text case & style converter', 'string/'),
            ('Text diff tool', 'diff/'),
            ('Case converter (camel/snake/kebab)', 'case/'),
            ('UUID & random data generator', 'generator/'),
            ('Are the pattern and text I test saved?',
             'No. Matching runs locally in your browser; the page has no code that sends your pattern or test text to a server. You can keep testing offline (the first load needs the network for page resources).'),
            ('Are the pattern and text I test saved?',
             'No. Matching runs locally in your browser; the page has no code that sends your pattern or test text to a server. You can keep testing offline (the first load needs the network for page resources).'),
            ('Are the pattern and text I test saved?',
             'No. Matching runs locally in your browser; the page has no code that sends your pattern or test text to a server. You can keep testing offline (the first load needs the network for page resources).'),
        ],

    },
    'timestamp': {
        'nav': 'Timestamp',
        'title': 'Unix Timestamp to Date Converter — Seconds & ms | DevTools',
        'description': (
            'Convert Unix timestamps to dates and back, reading 10-digit values as seconds and 13-digit '
            'values as milliseconds, with ISO 8601, RFC 2822 and timezone output.'
        ),
        'keywords': (
            'unix timestamp,timestamp converter,epoch converter,timestamp to date,date to timestamp,'
            'milliseconds timestamp,iso 8601,rfc 2822,utc time'
        ),
        'h1': 'Unix Timestamp & Date Converter',
        'intro': [
            'The top of the page shows the current timestamp ticking in both seconds and milliseconds; '
            'below it you can convert in either direction — enter a timestamp to get a readable date, or '
            'pick a date and time to get the matching timestamp.',
            'Results come out in ISO 8601, RFC 2822, local and UTC formats, and you can switch between '
            'several common timezones to compare them.',
        ],
        'features': [
            ('Seconds or Milliseconds',
             'A 10-digit value is read as seconds and a 13-digit value as milliseconds, with no unit '
             'selector to fiddle with.'),
            ('Two-Way Conversion',
             'Timestamp to date and date to timestamp, both on the same page.'),
            ('Live Clock',
             'A continuously updating Unix timestamp in seconds and milliseconds, useful for checking '
             'drift between a server clock and your own.'),
            ('Timezone Comparison',
             'Switch between local time, UTC, Beijing, New York, London and Tokyo at any time.'),
            ('Standard Formats',
             'ISO 8601 and RFC 2822 side by side, the two formats you meet most often in logs and '
             'HTTP headers.'),
        ],
        'steps': [
            'Enter a 10- or 13-digit number under "Timestamp to date" and convert.',
            'Pick a date and time under "Date to timestamp" and convert to get both second and '
            'millisecond values.',
            'Use the timezone dropdown below to see the same instant in other zones.',
            'Switch the buttons at the top between ISO 8601, RFC 2822, local and UTC output.',
        ],
        'faq': [
            ('What is the difference between a 10-digit and a 13-digit timestamp?',
             'A 10-digit value counts seconds (Unix time) and a 13-digit value counts milliseconds. '
             'JavaScript Date.now() returns milliseconds, while backends and databases commonly store '
             'seconds; the two differ by a factor of 1000, and mixing them is one of the most common '
             'causes of timestamps that do not line up.'),
            ('What is the year 2038 problem?',
             'A signed 32-bit integer can hold Unix seconds only up to 2147483647, which is '
             '2038-01-19 03:14:07 UTC. Past that instant, systems still storing timestamps in a 32-bit '
             'int overflow. Today 64-bit systems and JavaScript are not affected.'),
            ('Do Unix timestamps include leap seconds?',
             'No. Unix time is counted in UTC at a fixed 86400 seconds per day, and leap seconds are '
             'smoothed over elsewhere by the operating system, so a timestamp never shows a 60th second.'),
            ('Why is the converted date a few hours off from my server logs?',
             'Almost always a timezone setting. A Unix timestamp is an absolute UTC value; whether you '
             'display it as local time or UTC only affects the presentation. Compare the two with the '
             'timezone switcher to confirm.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Cron expression generator', 'cron-generator/'),
            ('Batch timestamp converter', 'batch/'),
            ('Common timestamp lookup (today / this week / this month)', 'timestamp-list/'),
            ('World time zones & current time', 'timezones/'),
        ],
    },
    'hash': {
        'nav': 'Hash',
        'title': 'MD5 / SHA-256 Hash Generator — HMAC & Files | DevTools',
        'description': (
            'Compute MD5, SHA-1, SHA-256 and SHA-512 hashes of text or files, with HMAC and AES '
            'encryption, all in the browser. Nothing is uploaded to a server.'
        ),
        'keywords': (
            'md5 online,sha256 online,sha1,hash generator,file checksum,hmac,'
            'aes encrypt decrypt,file hash'
        ),
        'h1': 'MD5 / SHA-256 Hash & Checksum Tool',
        'intro': [
            'Type or paste some text, or pick a file, and get its hash for the algorithm you choose. '
            'MD5, SHA-1, SHA-256 and SHA-512 are all supported, alongside HMAC and AES encryption.',
            'All hashing happens in the browser and neither the text nor the file is uploaded, which is '
            'exactly what you need when verifying an installer or checking firmware.',
        ],
        'features': [
            ('Common Algorithms',
             'Switch between MD5, SHA-1, SHA-256 and SHA-512 with the result updating instantly.'),
            ('File Hashes',
             'Select a file and its checksum is computed automatically, so you can confirm a download '
             'arrived intact and untampered.'),
            ('HMAC',
             'Keyed message authentication codes for verifying both the origin and the integrity of a message.'),
            ('AES Encryption',
             'AES-CBC and AES-GCM modes for encrypting and decrypting text locally.'),
            ('Copy Result',
             'Copy the full hash with one click and drop it into a verification script or a ticket.'),
        ],
        'steps': [
            'Enter the text to hash on the left, or load a file with the file picker.',
            'Choose MD5, SHA-1, SHA-256, SHA-512 or another algorithm on the right.',
            'The result appears in the output box automatically; click Copy to take it.',
            'For HMAC or AES, fill in the key when prompted.',
        ],
        'faq': [
            ('Is MD5 still usable?',
             'MD5 collisions can be constructed deliberately, so it must not be used for signatures, '
             'certificates or password storage. It remains fine for non-adversarial integrity checks '
             'such as confirming a download completed, since it is faster than SHA-256 and almost every '
             'download page publishes MD5 values. For anything security-related, use SHA-256 or better.'),
            ('Is it safe to compute hashes here?',
             'Yes. The computation runs entirely inside your browser and neither the text nor the file '
             'leaves your machine. That said, if you are handling sensitive data in an untrusted '
             'environment, a local command-line tool is still the safer choice, since browser extensions '
             'or page scripts can add risk.'),
            ('Why is a SHA-256 hash 64 characters long?',
             'SHA-256 produces a 256-bit digest, and hexadecimal notation uses two characters per byte, '
             'so 32 bytes x 2 = 64 characters. By the same logic SHA-512 gives 128 characters and '
             'MD5 gives 32.'),
            ('Why does the same string always produce the same hash?',
             'Hash functions are deterministic: the same input must produce the same output, and that is '
             'precisely what makes them useful for verification. If you need unpredictable output, add a '
             'random salt to the input.'),
            ('Is the content or file I hash uploaded?',
             'No. MD5, SHA and HMAC computation runs entirely in your browser, and files are handled through the local file reading API — nothing leaves your device. The tool works offline.'),
        ],
        'seealso': [
            ('Base64 / URL / Unicode codec', 'encode/'),
            ('JWT decoder & verifier', 'jwt/'),
            ('UUID generator & parser', 'uuid/'),
            ('Password & random data generator', 'generator/'),
        ],

    },
    'formatter': {
        'nav': 'Formatter',
        'title': 'HTML / CSS / JS / SQL Formatter & Minifier | DevTools',
        'description': (
            'Beautify or minify HTML, CSS, JavaScript, XML and SQL with 2-space, 4-space or tab '
            'indentation, and see the size before and after. Runs locally in your browser.'
        ),
        'keywords': (
            'html formatter,css formatter,js beautifier,javascript formatter,sql formatter,'
            'xml formatter,code minifier,code beautifier'
        ),
        'h1': 'HTML / CSS / JS / SQL Formatter',
        'intro': [
            'Paste minified or badly indented code, choose the language and format it into a readable '
            'structure with one click. It works the other way too: collapse code onto a single line to '
            'shrink payloads or squeeze it into a config value.',
            'Formatting happens in the browser and your source is never uploaded, so it is safe for '
            'internal code snippets.',
        ],
        'features': [
            ('Multiple Languages',
             'HTML, CSS, JavaScript, XML and SQL, the five formats you need most often.'),
            ('Format & Minify',
             'Expand code into readable indentation, or compress it into a compact single line.'),
            ('Indentation Choice',
             '2 spaces, 4 spaces or tabs, matching whatever your project uses.'),
            ('Size Comparison',
             'Shows the size before and after minifying so you can judge the saving.'),
            ('Sample Data',
             'Built-in samples let you try it out without hunting for a snippet first.'),
        ],
        'steps': [
            'Paste the code you want to process on the left.',
            'Choose the language on the right: HTML, CSS, JavaScript, SQL or XML.',
            'Pick an indentation style and click Format or Minify.',
            'Review the output in the result panel and click Copy.',
        ],
        'faq': [
            ('Does formatting change how my code behaves?',
             'For HTML, CSS, XML and SQL, formatting only adjusts whitespace and leaves semantics '
             'untouched. JavaScript deserves more care because of automatic semicolon insertion: joining '
             'two lines or moving a line break can change statement boundaries in a few rare constructs, '
             'so give the result a quick read afterwards.'),
            ('Can minified code be restored?',
             'Whitespace-only minification can be undone by formatting again, but optimisations such as '
             'variable renaming and dead code elimination are irreversible. This tool only removes '
             'whitespace and never renames identifiers.'),
            ('Which SQL dialects does the formatter support?',
             'It applies generic keyword casing and indentation, which handles the common syntax of '
             'MySQL, PostgreSQL and SQL Server. Dialect-specific constructs, such as certain stored '
             'procedure bodies, may not lay out perfectly.'),
            ('Is my code uploaded?',
             'No. All formatting is done locally in the browser and your code is never sent to a server.'),
            ('Does it format Go code?',
             'Not yet. Go ships with the official gofmt / goimports formatters, which are normally '
             'run in your editor or CI pipeline — see the Go command cheat sheet for usage, and our '
             'blog for a detailed comparison of the two tools.'),
        ],
        'seealso': [
            ('Go formatter online (gofmt)', 'gofmt-online/'),
            ('Go command cheat sheet (gofmt / goimports usage)', 'go-cheatsheet/'),
            ('Blog: gofmt vs goimports, and how to wire them into CI', 'blog/gofmt-vs-goimports/'),
        ],
    },
    'go-cheatsheet': {
        'nav': 'Go Cheat Sheet',
        'title': 'Go Command Cheat Sheet — build / mod / gofmt | DevTools',
        'description': (
            'A searchable Go toolchain cheat sheet: go build, go test, go mod tidy, go get, '
            'gofmt vs goimports, GOPROXY mirrors, GOPRIVATE, go.mod directives '
            '(require / replace / retract), GOOS/GOARCH cross-compilation and GOTOOLCHAIN. '
            'Every entry includes a copy-paste example and a real-world pitfall. Bilingual.'
        ),
        'keywords': (
            'go command cheat sheet,go mod tidy,go get,gofmt vs goimports,goproxy,'
            'go.mod replace,go cross compile,GOOS GOARCH,gotoolchain,go build flags,'
            'goprivate,go mod commands,go environment variables'
        ),
        'h1': 'Go Toolchain Command Cheat Sheet',
        'intro': [
            'A full-text searchable cheat sheet for the Go toolchain, organized into the six '
            'groups you reach for most: build & test (go build / go test), modules & dependencies '
            '(go mod tidy / go get), formatting (gofmt / goimports), key environment variables '
            '(GOPROXY / GOPRIVATE), go.mod directives (require / replace / retract), and '
            'cross-compilation & toolchain management.',
            'Every entry ships a copy-paste example plus a real-world pitfall — why the go test '
            'result cache makes "changed env var, same result" happen, why a vendor directory '
            'makes go get look broken, and why replace only works in the main module. '
            'Maintained against current Go releases; applies to Go 1.27.x.',
        ],
        'features': [
            ('Full-Text Search', 'The search box filters across commands, descriptions and '
             'pitfalls — type a keyword and jump straight to the entry.'),
            ('Six High-Frequency Groups', 'Build & test, dependencies, formatting, environment '
             'variables, go.mod directives and cross-compilation, each in its own section.'),
            ('Copy-Paste Examples', 'Every command comes with a working example, including a '
             'multi-platform cross-compilation matrix.'),
            ('Pitfalls Called Out', 'Each entry carries a "Watch out" note — the difference '
             'from ordinary documentation.'),
            ('Maintained Per Release', 'The applicable Go version and update date are shown; '
             'entries are reviewed after each Go release.'),
            ('Pure Static, No Signup', 'Content is baked into the page at build time — complete '
             'on first paint, no login, no ads, no tracking.'),
        ],
        'steps': [
            'Type a command or keyword (e.g. tidy, proxy, replace) into the search box to '
            'filter entries instantly.',
            'Or click a section tab to jump to a group: build / deps / formatting / env / '
            'go.mod / cross-compile.',
            'Copy the commands from the example blocks; the Watch-out note tells you when the '
            'result differs from expectations.',
            'Need to format HTML/CSS/JS/SQL online? Use the code formatter; for the gofmt vs '
            'goimports deep dive, see the blog.',
        ],
        'faq': [
            ('What is the difference between gofmt and goimports?',
             'gofmt only handles layout (indentation, alignment, spacing) and never touches '
             'imports; goimports builds on gofmt by adding/removing imports and sorting them '
             'into stdlib and third-party groups. Their output on the same file can differ — '
             'standardize on goimports -l in CI. See the blog post for the full comparison '
             'with CI configuration examples.'),
            ('How do I configure GOPROXY behind a restricted network?',
             'Run go env -w GOPROXY=https://goproxy.cn,direct (or another reachable mirror). '
             'The trailing direct means "fall back to the origin only after all proxies fail" '
             'and must come last; combine it with GOPRIVATE=git.company.com/* for private '
             'repositories so they skip the proxy and checksum database.'),
            ('What is the difference between go get and go install?',
             'go get only edits the current project\'s go.mod (add/upgrade/downgrade a '
             'dependency) and installs no binaries; go install pkg@version installs a command '
             'into GOBIN and ignores the go.mod of the current directory. Use go get for '
             'project dependencies and go install for global tools.'),
            ('Does cross-compiling require a target-platform toolchain?',
             'No. GOOS=linux GOARCH=arm64 go build is all it takes, and go tool dist list '
             'shows every supported pair. The only exception is CGO-based dependencies '
             '(such as some sqlite drivers), which need a target C toolchain or a pure-Go '
             'replacement.'),
            ('Do I still need to set GO111MODULE?',
             'No. It was the module-mode switch of the Go 1.11–1.22 era and was removed from '
             'the go command entirely in Go 1.23 — setting it has no effect. Delete '
             'GO111MODULE=on from legacy CI scripts.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Code formatter (HTML / CSS / JS / SQL)', 'formatter/'),
            ('Blog: gofmt vs goimports, and how to wire them into CI', 'blog/gofmt-vs-goimports/'),
            ('JSON formatter & validator', './'),
            ('Is my lookup recorded when I use the cheatsheet?',
             'No. The cheatsheet is a fully static page — every command, variable and note is baked into the HTML at build time. There are no search logs, no query records and no accounts.'),
            ('Is my lookup recorded when I use the cheatsheet?',
             'No. The cheatsheet is a fully static page — every command, variable and note is baked into the HTML at build time. There are no search logs, no query records and no accounts.'),
            ('Is my lookup recorded when I use the cheatsheet?',
             'No. The cheatsheet is a fully static page — every command, variable and note is baked into the HTML at build time. There are no search logs, no query records and no accounts.'),
        ],
    },
    'string': {
        'nav': 'Strings',
        'title': 'String & Text Tools — Case, Sort, Dedupe & Count | DevTools',
        'description': (
            'Convert case and naming style, sort, dedupe, find and replace, split or join text and add '
            'line numbers, with live character, word, line and byte counts.'
        ),
        'keywords': (
            'string tools,text dedupe,text sorter,case converter,camelcase converter,'
            'character counter,text replace,remove duplicate lines'
        ),
        'h1': 'Online String & Text Tools',
        'intro': [
            'The everyday chores of tidying up text: change case, switch naming style, sort lines, remove '
            'duplicates, add prefixes in bulk, count characters. Type on the left, choose an operation on '
            'the right, and the result appears immediately.',
            'Processing happens locally in the browser and your text is never uploaded.',
        ],
        'features': [
            ('Case & Naming',
             'UPPER, lower and Title Case, plus conversion between camelCase, snake_case and other '
             'naming styles.'),
            ('Sorting',
             'Sort lines alphabetically, by length, or shuffle them randomly.'),
            ('Deduplication',
             'Remove duplicate lines, with options to keep or drop blank and whitespace-only lines.'),
            ('Find & Replace',
             'Plain text or regular expression replacement with a preview of what matched.'),
            ('Split & Join',
             'Split text by a delimiter or a fixed length, or join multiple lines into one.'),
            ('Line Operations',
             'Add a prefix, suffix or line number to every line, with a custom start value and format.'),
            ('Live Statistics',
             'Character, word, line and UTF-8 byte counts update as you type.'),
        ],
        'steps': [
            'Paste or type the text you want to work on the left.',
            'Pick an operation category on the right — case, sorting, dedupe, replace, split/join or '
            'line operations.',
            'Fill in any parameters the operation needs, such as a delimiter or prefix.',
            'Review the output in the result panel and copy it.',
        ],
        'faq': [
            ('How is the byte count calculated?',
             'As UTF-8. An ASCII character takes 1 byte, a common Chinese character takes 3, and emoji '
             'or other supplementary-plane characters usually take 4. That is why the byte count of '
             'non-Latin text is noticeably larger than its character count.'),
            ('Can I use regular expressions for find and replace?',
             'Yes. Choose the replace operation and use a regular expression, referencing capture groups '
             'as $1, $2 and so on.'),
            ('When deduplicating, is the first or the last occurrence kept?',
             'The first occurrence is kept by default and later duplicates are removed, so the relative '
             'order of the remaining lines is preserved.'),
            ('Does it slow down with very long text?',
             'Routine processing of up to tens of thousands of lines is instant. For much larger inputs '
             'it is better to work in chunks, so the browser does not have to build one enormous string.'),
            ('Is the text I process uploaded?',
             'No. Case conversion, de-duplication, sorting and counting all run in your browser; the page contains no code that sends your text anywhere. It works offline.'),
        ],
        'seealso': [
            ('Case converter (camel/snake/kebab)', 'case/'),
            ('Text diff tool', 'diff/'),
            ('Regex tester', 'regex/'),
            ('JSON formatter & validator', './'),
        ],

    },
    'generator': {
        'nav': 'Generators',
        'title': 'UUID, Password & QR Code Generator Online | DevTools',
        'description': (
            'Generate UUID v4 in bulk, strong random passwords, QR codes you can download as PNG, '
            'Lorem Ipsum placeholder text, number sequences and test data — all locally.'
        ),
        'keywords': (
            'uuid generator,online uuid,guid generator,random password generator,qr code generator,'
            'lorem ipsum,random data generator,test data'
        ),
        'h1': 'UUID / Password / QR Code Generator',
        'intro': [
            'A handful of generators you want within reach: UUIDs, random passwords, QR codes, '
            'placeholder text, number sequences and random test data. Configure the parameters on the '
            'left and generate on the right.',
            'UUIDs and passwords come from the browser cryptographic random source, and nothing is '
            'routed through a server.',
        ],
        'features': [
            ('UUID',
             'Generates UUID v4 values, one or many at a time, with per-item copy or copy-all support.'),
            ('Random Passwords',
             'Set the length and character set, toggling uppercase, lowercase, digits and symbols '
             'independently.'),
            ('QR Codes',
             'Turn text or a URL into a QR code, adjust the size and colours, and download it as a PNG.'),
            ('Lorem Ipsum',
             'Generate placeholder text by paragraph, sentence or word count for layout previews.'),
            ('Number Sequences',
             'Produce arithmetic sequences with a chosen start, end and step, or random numbers within '
             'a range.'),
            ('Random Test Data',
             'Bulk-generate names, email addresses, phone numbers, addresses and ID numbers for testing.'),
        ],
        'steps': [
            'Choose the generator you want on the right: UUID, random password, QR code and so on.',
            'Adjust length, character set and quantity in the parameter panel on the left.',
            'Click Generate to produce the results.',
            'Use Copy to take the output, or download a QR code directly as a PNG.',
        ],
        'faq': [
            ('Can UUID v4 values collide?',
             'A UUID v4 carries 122 random bits, so collisions are theoretically possible but '
             'astronomically unlikely: generating a billion of them every second for about 100 years '
             'still leaves a collision probability far below the chance of a hardware failure. In '
             'practice you can treat them as unique.'),
            ('Are the generated passwords really random?',
             'Yes. They come from the browser crypto.getRandomValues() cryptographic random number '
             'generator rather than Math.random(), so there is no predictable pseudo-random sequence. '
             'Store the result somewhere trustworthy — this page keeps no record of it.'),
            ('Can the generated test data be used in production?',
             'No. Fields such as phone and ID numbers are fabricated to match a format and suit only '
             'testing and demos. They are not real, and may coincidentally match a real person.'),
            ('Are there restrictions on using the QR codes?',
             'The QR code format is an open standard and free to use. Do make sure the URL or content '
             'you encode is lawful — the code is only a carrier and does not change who is responsible '
             'for what it contains.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('UUID generator & parser', 'uuid/'),
            ('Snowflake ID decoder & builder', 'snowflake/'),
            ('MD5 / SHA / HMAC hashing', 'hash/'),
            ('Text case & style converter', 'string/'),
            ('Are generated passwords and random data recorded?',
             'No. UUIDs, random passwords and QR codes are all generated locally in your browser. The page records nothing, sends no requests and has no accounts — it works offline.'),
            ('Are generated passwords and random data recorded?',
             'No. UUIDs, random passwords and QR codes are all generated locally in your browser. The page records nothing, sends no requests and has no accounts — it works offline.'),
            ('Are generated passwords and random data recorded?',
             'No. UUIDs, random passwords and QR codes are all generated locally in your browser. The page records nothing, sends no requests and has no accounts — it works offline.'),
        ],

    },
    'hotnews': {
        'nav': 'Tech News',
        'title': "Today's Tech News — Live Headlines for Developers | DevTools",
        'description': (
            'A tech news page rebuilt automatically every day from Hacker News, TechCrunch, '
            'The Verge, Ars Technica and Joho no Todai. Every headline links straight to the original article. '
            'No signup, no ads, no tracking.'
        ),
        'keywords': (
            'tech news today,daily tech headlines,hacker news front page,developer news,'
            'tech news aggregator,techcrunch headlines,ars technica,the verge tech'
        ),
        'h1': "Today's Tech News for Developers",
        'intro': [
            'One page with the day\u2019s most useful technology reading. It pulls the public RSS '
            'feeds of Hacker News, TechCrunch, The Verge, Ars Technica and Joho no Todai into a single list, keeps '
            'the source\u2019s own ordering, and links every headline straight to the original '
            'article. Nothing is republished here — the copyright stays with each publisher.',
            'The list is refreshed and the page rebuilt once a day. Because the '
            'result is baked into plain HTML at build time rather than loaded by JavaScript, the '
            'page works with no API calls, loads in one request, and is fully readable by search '
            'engines and text browsers. There is no signup, no popup, no interstitial and no cookie.',
        ],
        'features': [
            ('Grouped by source',
             'Four sources, one section each. Use the tabs above the list to focus on a single '
             'publication, or leave it on All to read everything in order.'),
            ('Straight to the original',
             'Every headline is a direct link to the publisher, opened in a new tab with no '
             'redirect page and no tracking parameters added.'),
            ('Updated daily',
             'A scheduled job refetches every source and rebuilds the page each day, so what '
             'you open is always the current edition.'),
            ('Community signal',
             'Hacker News entries keep their point count, which is often the clearest read on how '
             'much the developer community actually cared about a story.'),
            ('Graceful fallback',
             'If a source is briefly unreachable the previous successful snapshot is kept and '
             'labelled with its timestamp, so the page never renders empty.'),
            ('No account, no app',
             'A plain static page. No registration, no install, no browser extension.'),
        ],
        'steps': [
            'Scroll the list below — by default every source is expanded, top to bottom.',
            'Click a source tab to narrow the list to one publication, or All to see everything.',
            'Click any headline to open the full article on the publisher\u2019s site in a new tab.',
            'Need an actual tool? Use the top navigation to jump to the JSON, regex or timestamp pages.',
        ],
        'faq': [
            ('How often is this page updated?',
             'Once a day. The scheduled job refetches every source and rebuilds the '
             'page, so everyone sees the same edition at the same time. The exact timestamp is '
             'printed at the top of the list.'),
            ('Did you write these articles?',
             'No. This page only reads each publisher\u2019s public RSS summary and displays the '
             'headline, summary and publish time. The full article and its copyright belong to the '
             'publisher, and clicking a headline takes you there. If a publisher would rather not '
             'be aggregated, the feedback button removes them on request.'),
            ('Why is the ordering not by time?',
             'Each source\u2019s own order is preserved. Those lists are already ranked by editors '
             'or by an algorithm — most visibly on Hacker News, where re-sorting by timestamp would '
             'destroy the meaning of the ranking.'),
            ('Do the outbound links carry ads or redirects?',
             'No. Headlines point directly at the article URL. This site adds no interstitial, no '
             'affiliate parameters and no redirect layer.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Common timestamp lookup (today / this week / this month)', 'timestamp-list/'),
            ('Unix timestamp converter', 'timestamp/'),
            ('Go toolchain cheatsheet', 'go-cheatsheet/'),
            ('JSON formatter & validator', './'),
        ],

    },
    'color': {
        'nav': 'Color',
        'title': 'Color Converter — Hex / RGB / HSL / CSS Name | DevTools',
        'description': (
            'Convert colors between Hex, RGB, HSL and CSS color names with a live preview. '
            'Supports 3/6/8-digit Hex, rgb()/rgba(), hsl()/hsla() and all 148 CSS named colors. '
            'Everything runs locally in your browser.'
        ),
        'keywords': 'color converter,hex to rgb,rgb to hsl,css color name,online color converter,hex color,rgb color',
        'h1': 'Color Converter (Hex / RGB / HSL / Name)',
        'intro': [
            'Type any color and the tool shows the other three representations plus the matching CSS '
            'color name, with a live swatch. It accepts #rgb, #rrggbb, #rrggbbaa, rgb()/rgba(), '
            'hsl()/hsla() and named colors like red or rebeccapurple.',
            'All conversion happens in your browser — no color value is ever sent anywhere.',
        ],
        'features': [
            ('Bidirectional', 'Switch between Hex, RGB, HSL and CSS name; all four update together.'),
            ('Name lookup', 'Recognises the 148 standard CSS named colors and finds a name for any color.'),
            ('Live preview', 'The swatch updates as you type, flipping text contrast for light or dark colors.'),
            ('Alpha channel', '8-digit Hex and rgba() alpha values are kept through conversion.'),
        ],
        'steps': [
            'Enter a color on the left — #ff0000, rgb(255,0,0), hsl(0,100%,50%) or red.',
            'The right side shows Hex, RGB, HSL and the name together.',
            'Click Copy to take the format you need.',
        ],
        'faq': [
            ('What is the difference between Hex and RGB?',
             'They are two notations for the same color: Hex is base-16, RGB is base-10. '
             '#ff0000 and rgb(255,0,0) are the identical red, just written differently.'),
            ('What is the last pair in 8-digit Hex?',
             'It is the alpha (transparency) channel — two Hex digits for 0..255, matching the '
             'fourth argument of rgba(): 00 is fully transparent and ff is fully opaque.'),
            ('Why do some colors show no name?',
             'CSS only defines 148 named colors such as red, blue and rebeccapurple. Most colors '
             'have no English name, so this field shows "-" — use Hex/RGB/HSL instead.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Hex to Binary / Decimal', 'hex/'),
            ('Any-Base Converter', 'base/'),
            ('Are the color values I pick uploaded?',
             'No. HEX / RGB / HSL parsing and conversion run entirely in your browser; the page has no code that sends color values anywhere. The picker only reads values you paste or type — it never touches your photo library.'),
        ],
    },
    'case': {
        'nav': 'Case style',
        'title': 'Case Converter — camel/snake/kebab/Pascal Online | DevTools',
        'description': (
            'Convert identifiers between camelCase, snake_case, kebab-case, PascalCase and '
            'CONSTANT_CASE. Auto-splits camelCase and underscores, handles digit boundaries, '
            'and runs entirely in your browser.'
        ),
        'keywords': 'case converter,camelCase converter,snake_case converter,kebab-case,PascalCase,variable naming',
        'h1': 'Case Style Converter',
        'intro': [
            'Re-pack an identifier into the target style after splitting it into words: camelCase, '
            'snake_case, kebab-case, PascalCase or CONSTANT_CASE. Handy when renaming legacy code or '
            'matching a different language SDK.',
            'Splitting recognises camelCase boundaries, underscores, hyphens and digit/letter edges; '
            'everything stays local to the browser.',
        ],
        'features': [
            ('Five styles', 'One click between camelCase, snake_case, kebab-case, PascalCase, CONSTANT_CASE.'),
            ('Smart split', 'Detects camelCase, underscores, hyphens and digit edges without mangling myVar.'),
            ('Live', 'Converts as you type — no button needed to see the result.'),
            ('Copy', 'Copy the converted identifier straight from the result panel.'),
        ],
        'steps': [
            'Enter text on the left, e.g. my_variable_name or MyVariableName.',
            'Pick the target style on the right.',
            'The result updates instantly; click Copy to take it.',
        ],
        'faq': [
            ('How are digits handled?',
             'Digits are treated as their own word segment — v2api splits into v, 2, api, so the '
             'number is preserved intact rather than glued to a neighbouring letter.'),
            ('CONSTANT_CASE vs snake_case?',
             'Both separate words with underscores; CONSTANT_CASE is all uppercase (used for macros, '
             'constants and enums), while snake_case is all lowercase (common for Python names).'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Text case & style converter', 'string/'),
            ('Regex tester', 'regex/'),
            ('Go formatter online (gofmt)', 'gofmt-online/'),
            ('JSON formatter & validator', './'),
            ('Is the text I convert uploaded?',
             'No. Name-style detection and conversion run entirely in your browser; the page contains no code that sends your text anywhere. It works offline.'),
        ],

    },
    'jwt': {
        'nav': 'JWT decoder',
        'title': 'JWT Decoder — Parse Header/Payload, Check Expiry | DevTools',
        'description': (
            'Decode JWTs online: parse the Header and Payload, turn exp/iat/nbf into readable times, '
            'and verify HS256/384/512 signatures with a secret. Decoding and verification happen '
            'locally in your browser.'
        ),
        'keywords': 'jwt decoder,jwt parser,jwt verifier,jwt expiry,jwt online,json web token,hs256 verify',
        'h1': 'JWT Decoder & Signature Verifier',
        'intro': [
            'Paste a JWT (three dot-separated segments) to decode the Header and Payload JSON and turn '
            'exp (expiry), iat (issued at) and nbf (not before) into readable UTC times.',
            'For HS256/384/512 tokens, supply the secret to verify the signature locally. Decoding and '
            'verification run in your browser — the token and secret never leave your device.',
        ],
        'features': [
            ('Header / Payload', 'base64url-decode both segments and pretty-print them for inspection.'),
            ('Readable times', 'exp/iat/nbf become ISO 8601 times so you can see expiry at a glance.'),
            ('Symmetric verify', 'With a secret, verify HS256/384/512 signatures locally, live.'),
            ('Local first', 'No backend involved; token and secret are processed only on your device.'),
        ],
        'steps': [
            'Paste the full JWT (three segments joined by ".") on the left.',
            'The decoded Header, Payload and time fields appear on the right immediately.',
            'To verify a signature, enter the HS algorithm secret in the Signature verification box.',
        ],
        'faq': [
            ('Does decoding a JWT prove identity?',
             'No. Decoding only makes the content readable; anyone can decode a JWT. Trust depends on '
             'the server checking the signature with its key. This tool only does a local HS verification '
             'when you provide a secret; RS/ES algorithms are not verified here.'),
            ('Why does it still say not verified with a secret?',
             'Only alg values of HS256/384/512 are verified with the secret. For RS256/ES256 and other '
             'asymmetric algorithms the signature must be checked with a public key on the server, which '
             'the browser cannot do safely — the tool says so explicitly.'),
            ('If exp has passed, is it definitely invalid?',
             'Yes, exp is the expiry time and servers reject expired tokens. This tool only decodes and '
             'displays; whether a token is accepted is always up to your server.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('MD5 / SHA / HMAC hashing', 'hash/'),
            ('Base64 / URL / Unicode codec', 'encode/'),
            ('Unix timestamp converter', 'timestamp/'),
            ('JSON formatter & validator', './'),
            ('Is the token I parse uploaded?',
             'No. JWT decoding and HS256 / 384 / 512 signature verification all run in your browser — the token never leaves your device. That matters most for production tokens with sensitive claims.'),
        ],

    },
    'yaml': {
        'nav': 'JSON ↔ YAML',
        'title': 'JSON ↔ YAML Converter Online — Both Ways, Private | DevTools',
        'description': (
            'Convert between JSON and YAML online: JSON to YAML and YAML to JSON, preserving structure. '
            'Parsed with js-yaml and processed locally in your browser.'
        ),
        'keywords': 'json to yaml,yaml to json,json yaml converter,online yaml,json to yml,yaml formatter',
        'h1': 'JSON ↔ YAML Converter',
        'intro': [
            'Enter JSON or YAML on the left, pick a direction, and get the other notation. Useful for '
            'turning API JSON into readable YAML config, or turning YAML config back into parseable JSON.',
            'Conversion uses the js-yaml library loaded in your browser; no text is uploaded.',
        ],
        'features': [
            ('Two-way', 'Swap between JSON → YAML and YAML → JSON with one click.'),
            ('Faithful', 'Objects, arrays, nesting, booleans and nulls are all preserved.'),
            ('Instant', 'Converts as you type; parse errors point at the problem.'),
        ],
        'steps': [
            'Enter JSON or YAML on the left.',
            'Pick the direction on the right.',
            'The result appears instantly; click Copy to take it.',
        ],
        'faq': [
            ('Are YAML and JSON losslessly convertible?',
             'Mostly. YAML is a superset of JSON, so anything JSON expresses is valid YAML. But YAML '
             'anchors, multi-document streams and complex type tags have no JSON equivalent and may be '
             'lost when converted.'),
            ('Does conversion need a network?',
             'No. The js-yaml parser is served from this site\u2019s own domain alongside the page, with no '
             'third-party CDN involved; the whole conversion runs locally in your browser.'),
            ('Is the YAML / JSON I convert uploaded?',
             'No. YAML parsing and JSON serialisation run in the js-yaml library inside your browser; the page has no code that sends your configuration anywhere. Feel free to use it offline with config files that contain secrets.'),
        ],
        'seealso': [
            ('JSON ↔ CSV / XML converter', './'),
            ('JSON ↔ TOML converter', 'toml/'),
            ('CSV viewer & converter', 'csv/'),
            ('CSV to SQL INSERT generator', 'csv-to-sql-insert/'),
        ],

    },
    'toml': {
        'nav': 'JSON ↔ TOML',
        'title': 'TOML to JSON Converter Online — Private | DevTools',
        'description': (
            'Convert between JSON and TOML online: JSON to TOML and TOML to JSON, suited to Go / Rust '
            'config files. Parsed with @iarna/toml and processed locally in your browser.'
        ),
        'keywords': 'json to toml,toml to json,json toml converter,online toml,toml formatter,go config',
        'h1': 'JSON ↔ TOML Converter',
        'intro': [
            'Enter JSON or TOML on the left, pick a direction, and get the other notation. TOML is the '
            'config format behind Go and Rust projects (e.g. Cargo.toml); converting to and from JSON '
            'makes it easy to move data between editors, APIs and config files.',
            'Conversion uses the @iarna/toml library loaded in your browser; no text is uploaded.',
        ],
        'features': [
            ('Two-way', 'Swap between JSON → TOML and TOML → JSON with one click.'),
            ('Config friendly', 'Tailored to config files in Go / Rust projects.'),
            ('Instant', 'Converts as you type; parse errors point at the problem.'),
        ],
        'steps': [
            'Enter JSON or TOML on the left.',
            'Pick the direction on the right.',
            'The result appears instantly; click Copy to take it.',
        ],
        'faq': [
            ('Is TOML better than JSON for config?',
             'For config it is often clearer: comments, unquoted keys and explicit grouping (tables) '
             'mean fewer braces and quotes than JSON, and none of YAML\u2019s indentation traps — which '
             'is why many language templates adopt it by default.'),
            ('Does conversion need a network?',
             'No. The @iarna/toml parser is served from this site\u2019s own domain alongside the page, '
             'with no third-party CDN involved; the whole conversion runs locally in your browser.'),
            ('Is the TOML / JSON I convert uploaded?',
             'No. TOML parsing and JSON serialisation run in a library inside your browser. Your configuration never leaves the device and the tool works offline.'),
        ],
        'seealso': [
            ('JSON ↔ YAML converter', 'yaml/'),
            ('JSON ↔ CSV / XML converter', './'),
            ('CSV viewer & converter', 'csv/'),
            ('Code formatter (HTML / CSS / JS / SQL)', 'formatter/'),
        ],

    },
    'csv': {
        'nav': 'JSON ↔ CSV',
        'title': 'JSON ↔ CSV Converter Online — Both Ways, Private | DevTools',
        'description': (
            'Convert between JSON and CSV online: JSON arrays (of objects or 2-D arrays) to CSV, and '
            'CSV back to JSON using the first row as header. Handles quoting and comma escaping, all '
            'locally in your browser.'
        ),
        'keywords': 'json to csv,csv to json,json array to csv,csv to json objects,online csv,table converter',
        'h1': 'JSON ↔ CSV Converter',
        'intro': [
            'Turn a JSON array (of objects or 2-D arrays) into CSV, or turn CSV back into a JSON array '
            'of objects using the first row as the header — handy for moving data between spreadsheets '
            'and programs.',
            'Fields containing commas, quotes or newlines are quoted correctly, so the result pastes '
            'cleanly into Excel or a database import script.',
        ],
        'features': [
            ('Two-way', 'Swap between JSON → CSV and CSV → JSON with one click.'),
            ('Auto header', 'CSV → JSON treats the first row as field names, one object per remaining row.'),
            ('Safe escaping', 'Commas, quotes and newlines inside a field are quoted properly.'),
        ],
        'steps': [
            'Enter a JSON array or CSV text on the left.',
            'Pick the direction on the right.',
            'The result appears instantly; click Copy to take it.',
        ],
        'faq': [
            ('How is the header determined for CSV → JSON?',
             'The first CSV row is taken as field names (the header), and each later row becomes one '
             'object. Rows with fewer columns than the header get empty strings so the JSON stays '
             'structurally complete.'),
            ('What column order is used for JSON → CSV?',
             'Columns follow the keys of the first object; extra keys from later objects are appended '
             'at the end, keeping the table tidy without dropping data.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('CSV to SQL INSERT generator', 'csv-to-sql-insert/'),
            ('JSON ↔ CSV / XML / YAML converter (JSON toolbox)', './'),
            ('JSON ↔ YAML converter', 'yaml/'),
            ('JSON ↔ TOML converter', 'toml/'),
            ('Is my CSV data uploaded?',
             'No. CSV parsing, viewing and JSON conversion all run in your browser — the data never leaves your device. Feel free to use it offline with exports that contain business data.'),
        ],
    },
    'batch': {
        'nav': 'Batch TS',
        'title': 'Batch Timestamp Converter — Bulk Convert, CSV Out | DevTools',
        'description': (
            'Bulk-convert Unix timestamps online: paste many timestamps or dates at once to convert '
            'between seconds/milliseconds timestamps and dates, with timezone selection and '
            'CSV-style table output. All processed locally in your browser.'
        ),
        'keywords': 'batch timestamp,timestamp batch,bulk timestamp,batch date converter,timestamp to date bulk,unix timestamp batch',
        'h1': 'Batch Timestamp & Date Conversion',
        'intro': [
            'Paste multiple timestamps or dates, one per line, choose the direction (timestamp → date '
            'or date → timestamp) and a time zone, and the results appear instantly in a table you can '
            'copy or export. Handy for logs, exported data tables and bulk API parameters.',
            'Every conversion runs in your browser, so nothing you paste is sent to any server.',
        ],
        'features': [
            ('Bulk both ways', 'One input per line; seconds and milliseconds are auto-detected; dates accept "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD".'),
            ('Time zone options', 'Results are interpreted and shown in local time, UTC, Beijing, New York, London, Tokyo and more.'),
            ('Table output', 'Results render as a two-column table; invalid rows are flagged in red for easy checking.'),
            ('Local first', 'No backend is involved, so even large batches never leave your device.'),
        ],
        'steps': [
            'Paste one timestamp or date per line in the left text box.',
            'Choose the conversion direction and time zone above.',
            'Results show instantly in the right-hand table; click "Copy" to take them.',
        ],
        'faq': [
            ('How much data can the batch converter handle?',
             'It depends on browser memory; a few thousand rows usually convert instantly. For very large inputs, paste in chunks to avoid building one huge table at once.'),
            ('What happens to a row with the wrong date format?',
             'Unparseable rows are flagged in red and marked "invalid"; the other valid rows still convert, so the whole batch does not fail.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Unix Timestamp & Date Converter (single)', 'timestamp/'),
            ('Timestamp cheat sheet', 'timestamp-list/'),
            ('World time zones & current time', 'timezones/'),
            ('Are the timestamps I batch-convert uploaded?',
             'No. Batch parsing and date conversion run entirely in your browser; the page has no code that sends your timestamps anywhere. It works offline.'),
        ],
    },
    'timestamp-list': {
        'nav': 'TS Reference',
        'title': 'Timestamp Cheat Sheet — Common Values in s & ms | DevTools',
        'description': (
            'Timestamp cheat sheet: seconds and milliseconds Unix timestamps plus the matching date '
            'for common reference points — now, start of today, this Monday, 1st of month, start of '
            'year, +1h, +7d, the 2038 limit and the epoch. Computed locally.'
        ),
        'keywords': 'timestamp cheat sheet,timestamp reference,unix timestamp table,common timestamps,millisecond timestamps,2038 timestamp',
        'h1': 'Timestamp Cheat Sheet',
        'intro': [
            'When writing code you often need fixed timestamps: the current second, midnight today, the '
            '2038 limit 2147483647... This sheet lists common reference points once, with their '
            'seconds, milliseconds and readable date, updating instantly when you switch time zone.',
            'Values are computed locally in your browser and need no network.',
        ],
        'features': [
            ('Common anchors', 'Covers now, start of today / this week / this month / this year, +1h, +7d, +1y, the 2038 limit and the epoch start.'),
            ('Two units', 'Each anchor shows both the seconds and the milliseconds timestamp.'),
            ('Time zone switch', 'Anchors like "midnight today" are interpreted in the time zone you pick.'),
        ],
        'steps': [
            'Pick a time zone in the dropdown.',
            'The table shows each anchor\'s seconds, milliseconds and date instantly.',
        ],
        'faq': [
            ('Which time zone is "midnight today" computed in?',
             'The time zone you select. "Local time" means your browser\'s zone; "UTC" means midnight UTC.'),
            ('What is the 2038 limit?',
             'The largest seconds timestamp a signed 32-bit integer can hold is 2147483647, which is '
             '2038-01-19 03:14:07 UTC. Systems past that overflow — this is the year-2038 problem.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Unix Timestamp & Date Converter', 'timestamp/'),
            ('Batch timestamp conversion', 'batch/'),
            ('Does this cheat sheet record my lookups?',
             'No. The page is static HTML — today, this week, this month and other common timestamps are computed at build time and baked in. There are no lookup records and no accounts.'),
            ('Does this cheat sheet record my lookups?',
             'No. The page is static HTML — today, this week, this month and other common timestamps are computed at build time and baked in. There are no lookup records and no accounts.'),
            ('Does this cheat sheet record my lookups?',
             'No. The page is static HTML — today, this week, this month and other common timestamps are computed at build time and baked in. There are no lookup records and no accounts.'),
        ],
    },
    'timezones': {
        'nav': 'Time Zones',
        'title': 'World Time Zones — UTC Offset & Current Time | DevTools',
        'description': (
            'World time zone reference: UTC offset and current time for UTC, Beijing, Tokyo, London, '
            'New York, Paris, Sydney and other major zones, with automatic daylight-saving adjustment, '
            'refreshed every second. Computed locally.'
        ),
        'keywords': 'time zone converter,world time zones,time zone reference,utc offset,time difference,daylight saving,current time by zone',
        'h1': 'World Time Zones & Current Time',
        'intro': [
            'When collaborating across zones, the annoying part is working out "what time is it for '
            'them". This table lists each major zone\'s current UTC offset and local time together, and '
            'handles daylight saving automatically — you do not need to remember who moves the clock an '
            'hour each season.',
            'Times are computed locally in your browser and refreshed every second, with no network needed.',
        ],
        'features': [
            ('Major zones', 'Covers UTC and 14 common IANA zones across China, Japan, India, Europe and the Americas.'),
            ('Automatic DST', 'Offsets follow the current date\'s daylight-saving rules; no manual add or subtract.'),
            ('Live refresh', 'Current time updates every second for direct comparison.'),
        ],
        'steps': [
            'The table already lists each zone\'s offset and current time.',
            'For another zone, convert by its IANA name or send feedback to add it.',
        ],
        'faq': [
            ('Why does the offset sometimes change?',
             'Regions with daylight saving move the clock forward an hour in summer, so the same '
             'zone\'s UTC offset differs by month. The page applies the current-date rule automatically.'),
            ('Are "UTC" and "GMT" the same?',
             'For everyday use, essentially yes; strictly, UTC is atomic-clock based and GMT is '
             'astronomical, and they agree to the second. This site labels offsets with UTC.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Unix Timestamp & Date Converter', 'timestamp/'),
            ('World clock', 'world-clock/'),
            ('Are the time zones I select uploaded?',
             "No. Conversions use the browser's built-in time zone database locally; the page has no code that sends your city or time selections anywhere. It works offline."),
        ],
    },
    'weeknumbers': {
        'nav': 'ISO Week',
        'title': 'ISO 8601 Week Number — Current Week & Year | DevTools',
        'description': (
            'ISO 8601 week number lookup: shows the current ISO week number and the ISO week-year '
            '(week starts Monday) in real time. Computed locally, refreshed each minute.'
        ),
        'keywords': 'iso week number,iso 8601 week,current week number,iso week year,week number calculator,iso week number',
        'h1': 'Current ISO 8601 Week Number',
        'intro': [
            'ISO 8601 puts Monday at the start of the week and defines week 1 as the week containing the '
            'first Thursday of the year — which means a few days at the start of January may belong to '
            'week 52 or 53 of the previous year. This tool matches the week numbering of many European systems.',
            'The week number is computed locally and refreshes each minute (auto-updates across week boundaries).',
        ],
        'features': [
            ('ISO 8601 compliant', 'Monday-start, Thursday-rule week numbering, consistent with European enterprise systems.'),
            ('Week-year shown', 'Also shows the ISO week-year the week belongs to (which may differ from the calendar year).'),
            ('Live refresh', 'Updates automatically across week boundaries.'),
        ],
        'steps': [
            'Open the page to see the current ISO week number and week-year.',
        ],
        'faq': [
            ('Why can January 1 show week 52?',
             'By the Thursday rule, if Jan 1 is Fri/Sat/Sun, most of its week falls in the previous '
             'year, so it is counted as week 52 or 53 of that year — which is why the ISO week-year can '
             'differ from the calendar year.'),
            ('How is the ISO week number different from the common one?',
             'Many US-style systems start the week on Sunday and count the week containing Jan 1 as week '
             '1; ISO starts on Monday and uses the Thursday rule, so the two can differ by a week at year start/end.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Current day of the year', 'daynumbers/'),
            ('Leap years & days per year', 'years/'),
            ('Are the dates I look up recorded?',
             'No. Week-number calculation runs locally in your browser; the page has no code that sends your dates anywhere and keeps no lookup records.'),
            ('Are the dates I look up recorded?',
             'No. Week-number calculation runs locally in your browser; the page has no code that sends your dates anywhere and keeps no lookup records.'),
            ('Are the dates I look up recorded?',
             'No. Week-number calculation runs locally in your browser; the page has no code that sends your dates anywhere and keeps no lookup records.'),
        ],
    },
    'daynumbers': {
        'nav': 'Day of Year',
        'title': 'Day of the Year — Current Day Number | DevTools',
        'description': (
            'Compute which day of the year the current date is (1–366). Leap years are detected '
            'automatically and the result refreshes live. Computed locally.'
        ),
        'keywords': 'day of year,current day number,julian day,days into the year,leap year days,day number',
        'h1': 'Current Day of the Year',
        'intro': [
            'Counting from January 1 (day 1), how many days have passed to today — a common year has 365 '
            'days, a leap year 366. This day count appears in some log formats, fiscal quarters and '
            'astronomical calculations.',
            'The value is computed locally and refreshes each minute.',
        ],
        'features': [
            ('Auto leap year', 'Leap years (366 days) and common years (365 days) are detected automatically.'),
            ('Live refresh', 'Updates automatically across day boundaries.'),
        ],
        'steps': [
            'Open the page to see the current day of the year.',
        ],
        'faq': [
            ('Is this the same as a "Julian day"?',
             'No. Here it is "day of the year" (restarting at 1 each year); a Julian day is a '
             'continuous count from 4713 BCE, not reset annually, and is used in astronomy and historiography.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('ISO 8601 week number', 'weeknumbers/'),
            ('Leap years & days per year', 'years/'),
            ('Are the dates I look up recorded?',
             'No. Day-of-year and day-remaining calculations run locally in your browser; the page has no code that sends your dates anywhere.'),
            ('Are the dates I look up recorded?',
             'No. Day-of-year and day-remaining calculations run locally in your browser; the page has no code that sends your dates anywhere.'),
            ('Are the dates I look up recorded?',
             'No. Day-of-year and day-remaining calculations run locally in your browser; the page has no code that sends your dates anywhere.'),
        ],
    },
    'years': {
        'nav': 'Leap Year',
        'title': 'Leap Year Lookup — Leap Years 1800–2100 | DevTools',
        'description': (
            'Leap year lookup: lists whether each year from 1800 to 2100 is a leap year, its day count '
            'and ISO starting week, and highlights the current year. Computed locally.'
        ),
        'keywords': 'leap year check,leap year list,common vs leap year,days per year,which years are leap,leap year calculator',
        'h1': 'Leap Years & Days per Year (1800–2100)',
        'intro': [
            'Leap-year rule: divisible by 4 but not by 100, or divisible by 400. Such years have 366 '
            'days with 29 days in February; the rest are common years with 365. This table lists every '
            'year from 1800 to 2100 for quick checking.',
            'Data is computed locally in your browser.',
        ],
        'features': [
            ('Three-century span', 'Covers 1800–2100, enough for almost all historical and future date checks.'),
            ('Leap flag', 'Each year is marked "Leap / Common" with its day count.'),
            ('ISO start week', 'Shows which ISO week the first week of each year starts at.'),
        ],
        'steps': [
            'The page shows the full leap-year table on open, with the current year highlighted.',
        ],
        'faq': [
            ('Why is 1900 not a leap year?',
             'The leap rule has an exception: a year divisible by 100 must also be divisible by 400 to '
             'be a leap year. 1900 is divisible by 100 but not by 400, so it is a common year; 2000 is '
             'divisible by 400, so it is a leap year.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('ISO 8601 week number', 'weeknumbers/'),
            ('Current day of the year', 'daynumbers/'),
            ('Are the years I view recorded?',
             'No. Calendar data is baked into the page at build time; paging and viewing happen locally, with no lookup records.'),
            ('Are the years I view recorded?',
             'No. Calendar data is baked into the page at build time; paging and viewing happen locally, with no lookup records.'),
            ('Are the years I view recorded?',
             'No. Calendar data is baked into the page at build time; paging and viewing happen locally, with no lookup records.'),
        ],
    },
    'world-clock': {
        'nav': 'World Clock',
        'title': 'World Clock — Current Time in Major Cities | DevTools',
        'description': (
            'Online world clock: shows current time and UTC offset for UTC, Beijing, Tokyo, London, New '
            'York, Paris, Sydney and other major cities as analog clock faces or a list, refreshed every '
            'second with daylight saving. Computed locally.'
        ),
        'keywords': 'world clock,analog clock,clock faces,multi-city time,city time comparison,world time,online clock,time zone comparison',
        'h1': 'World Clock',
        'intro': [
            'Put the current time of multiple cities on one screen, so you can see at a glance "what time '
            'is it for them" before a cross-border meeting or remote collaboration. Each city gets a round '
            'analog dial with live hour, minute and second hands, labeled with the city name and time zone; '
            'offsets auto-adjust for daylight saving by the current date.',
            'There are 38 standard time zones in the world (counting distinct UTC offsets actually in use '
            'in 2026, from UTC−12 to UTC+14, including non-hour offsets like UTC+05:30 and UTC+05:45); if '
            'you also count daylight-saving shifts the number is about 50 per year, and the IANA database '
            'lists about 345 geographic zones. Below, all 38 zones are listed in UTC order with at least '
            'one major city each, and multiple important cities in a zone are listed together.',
            'All computation happens on your device.',
        ],
        'features': [
            ('Analog clock faces', 'A round dial per city with live hour, minute and second hands, labeled with city and time zone.'),
            ('Three views', 'Switch between clock, list and "All zones"; the All-zones view lists every one of the 38 world time zones in UTC order.'),
            ('Offset & DST', 'Each city shows its current UTC offset, with daylight saving handled automatically.'),
            ('Live refresh', 'Updates every second.'),
        ],
        'steps': [
            'Clock faces are shown by default; click "List" to switch to the comparison table, or "All zones" to see every zone in UTC order.',
        ],
        'faq': [
            ('Why is a city\'s offset different from last time I looked?',
             'Cities with daylight saving move the clock forward an hour in certain months, so the '
             'offset changes; the page handles it automatically.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('World time zones & current time', 'timezones/'),
            ('Unix Timestamp & Date Converter', 'timestamp/'),
            ('Are the cities I add uploaded?',
             'No. The world clock uses local system time and built-in time zone data. Your city list is kept only in browser localStorage — never synced to any server — and disappears when you clear your browser data.'),
        ],
    },
    'countdown': {
        'nav': 'Countdown',
        'title': 'Countdown to a Unix Timestamp | DevTools',
        'description': (
            'Online countdown: enter a Unix timestamp (seconds or milliseconds, auto-detected) to see in '
            'real time how long until that moment, or how long since. Supports a shareable link. Computed locally.'
        ),
        'keywords': 'countdown,timestamp countdown,unix countdown,time to timestamp,online timer,target countdown',
        'h1': 'Countdown to a Target Timestamp',
        'intro': [
            'Enter the timestamp of a future (or past) moment and the tool counts down in real time how '
            'many days / hours / minutes / seconds remain; if that moment has passed, it shows how long '
            'ago. You can also copy a share link with the target parameter so the other person opens the '
            'same target.',
            'All computation happens locally in your browser.',
        ],
        'features': [
            ('Seconds/ms auto-detect', '10 digits read as seconds, 13 as milliseconds — no manual switch.'),
            ('Live countdown', 'Days/hours/minutes/seconds remaining or elapsed, refreshed every second.'),
            ('Shareable link', 'Generates a link with ?target= so the recipient reproduces the same target.'),
        ],
        'steps': [
            'Enter the target timestamp in the input box.',
            'The page shows the countdown instantly.',
            'Click "Copy share link" to share the result page with others.',
        ],
        'faq': [
            ('The time shown when I open the share link differs from yours?',
             'The target timestamp in the link is an absolute UTC instant; the "time remaining" depends '
             'on the opener\'s local current time, so different people and times see different '
             'remainders, but the target moment itself is the same.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Unix Timestamp & Date Converter', 'timestamp/'),
            ('Date difference', 'date-difference/'),
            ('Are the countdowns I set uploaded?',
             'No. Countdowns are computed locally in your browser and events are kept only in browser localStorage — never synced to any server.'),
        ],
    },
    'date-difference': {
        'nav': 'Date Diff',
        'title': 'Date Difference Calculator — Days/Hours/Min/Sec | DevTools',
        'description': (
            'Online date difference: pick or enter two date-times and compute the interval between them '
            '(days, hours, minutes, seconds). Interpreted in local time zone. Computed locally.'
        ),
        'keywords': 'date difference,days between dates,date calculator,time difference,days calculator,date interval',
        'h1': 'Difference Between Two Dates',
        'intro': [
            'Enter a start and an end date-time and the tool computes how many days, hours, minutes and '
            'seconds lie between them. Common for project durations, remaining membership time and event intervals.',
            'Computation happens locally in your browser, with no network needed.',
        ],
        'features': [
            ('Absolute interval', 'Whichever date is earlier, the interval is always given as an absolute value.'),
            ('Down to the second', 'Shows days, hours, minutes, seconds and total seconds.'),
            ('Local time zone', 'Input date-times are interpreted in your browser\'s local time zone.'),
        ],
        'steps': [
            'Pick a start and an end date-time.',
            'The result shows the interval instantly.',
        ],
        'faq': [
            ('How are cross-time-zone inputs computed?',
             'The page interprets the entered date-time in your browser\'s local time zone. If you need '
             'it in another zone, convert it to your local wall-clock time first, then enter it.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Date add / subtract', 'date-calculator/'),
            ('Countdown', 'countdown/'),
            ('Are the dates I calculate with uploaded?',
             'No. Date-difference calculation runs locally in your browser; the page has no code that sends your dates anywhere. It works offline.'),
        ],
    },
    'date-calculator': {
        'nav': 'Date Calc',
        'title': 'Date Add / Subtract — Add/Sub Years/Months/Days | DevTools',
        'description': (
            'Online date add/subtract: add or subtract years, months and days from a base date, with '
            'automatic month-end and year-end handling (e.g. Feb 28 + 1 day = Mar 1). Computed locally.'
        ),
        'keywords': 'date add subtract,date calculator,add days to date,subtract days,date offset,add months',
        'h1': 'Date Add / Subtract',
        'intro': [
            'Given a base date, enter the years, months and days to add or subtract and the tool computes '
            'the target date and its timestamp. It handles month-end and year-end correctly: for example '
            'Feb 28 plus 1 day becomes Mar 1, and Dec 31 plus 1 year is still Dec 31.',
            'All computation happens in your browser.',
        ],
        'features': [
            ('Years/months/days separately', 'Three independent fields, any combination.'),
            ('Month-end clamp', 'E.g. Jan 31 plus 1 month becomes Feb 28/29, not an overflow into March.'),
            ('With timestamp', 'The result also gives the matching Unix seconds timestamp.'),
        ],
        'steps': [
            'Pick a base date.',
            'Enter the years / months / days to add or subtract (may be negative).',
            'The result shows the target date and timestamp instantly.',
        ],
        'faq': [
            ('Why is "Jan 31 plus 1 month" Feb 28, not Mar 3?',
             'February has no 31st, so adding a month directly would "overflow" into early March, which '
             'feels wrong in most cases. This tool clamps the day to the last day of the target month, '
             'giving Feb 28 (or 29 in a leap year).'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Date difference', 'date-difference/'),
            ('Leap years & days per year', 'years/'),
            ('Are the dates I calculate with uploaded?',
             'No. Date arithmetic runs locally in your browser; the page has no code that sends your dates anywhere. It works offline.'),
        ],
    },
    'duration': {
        'nav': 'Duration',
        'title': 'ISO 8601 Duration Converter — String ↔ Seconds | DevTools',
        'description': (
            'Online ISO 8601 duration converter: convert between a PnYnMnDTnHnMnS duration string and '
            'seconds. Supports P1W, PT1H30M and more. Computed locally.'
        ),
        'keywords': 'iso 8601 duration,duration converter,duration to seconds,seconds to duration,P1DT12H,iso duration',
        'h1': 'ISO 8601 Duration String ↔ Seconds',
        'intro': [
            'ISO 8601 expresses a duration as "PnYnMnDTnHnMnS": after P come years/months/weeks/days, '
            'after T come hours/minutes/seconds. This tool converts between that human-readable string '
            'and the seconds value machines use.',
            'Years use 365 days and months use 30 days as approximations (without a reference date the '
            'real month length is unknown). Computation is local.',
        ],
        'features': [
            ('Two-way', 'Duration string → seconds, seconds → duration string.'),
            ('Format friendly', 'Supports any combination of PnY/PnM/PnW/PnD and TnH/TnM/TnS, e.g. P1W, PT1H30M.'),
            ('Instant validation', 'Flags an illegal format immediately.'),
        ],
        'steps': [
            'Enter a duration string (e.g. P1DT12H) in the top box to get seconds.',
            'Enter seconds in the bottom box to get an ISO duration string.',
        ],
        'faq': [
            ('Why is "1 month" only approximate in seconds?',
             'Different months have different lengths (28/29/30/31), and without a specific reference '
             'date the real month length cannot be determined, so this tool uses 30 days; years and '
             'months are for rough conversion only — for exact durations use days/hours/minutes/seconds.'),
            ('Can P1Y2M3DT4H5M6S be round-tripped?',
             'Yes. As long as you do not mix approximate units like month/year, the round trip is '
             'consistent and exact; conversions involving years/months carry rounding error from the approximation.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Unix Timestamp & Date Converter', 'timestamp/'),
            ('Date difference', 'date-difference/'),
            ('Are the durations I calculate with uploaded?',
             'No. ISO 8601 duration and seconds conversion runs locally in your browser; the page has no code that sends your durations anywhere.'),
        ],
    },
    'uuid': {
        'nav': 'UUID',
        'title': 'UUID Generator & Parser — v1/v4, Timestamp | DevTools',
        'description': (
            'Parse any UUID online: detect version (v1/v3/v4/v5) and variant (RFC4122, etc.), recover '
            'the timestamp and node for v1, and generate RFC4122 v4 UUIDs. All processing is local in your browser.'
        ),
        'keywords': 'uuid parser,uuid generator,uuid v4,uuid online,uuid timestamp,uuid version,uuid validate',
        'h1': 'UUID Parser and Generator',
        'intro': [
            'Paste a UUID to see its version (v1/v3/v4/v5) and variant (RFC4122 and others). For v1 UUIDs '
            'you also get the creation timestamp and the 48-bit node.',
            'Click "Generate v4" for a fresh RFC4122 random UUID. Everything runs locally, so nothing you '
            'paste leaves your device.',
        ],
        'features': [
            ('Version and variant', 'Automatically detects the UUID version (1/3/4/5) and variant (RFC4122, Microsoft, reserved).'),
            ('v1 timestamp', 'Recovers the 100-nanosecond creation timestamp and 48-bit node of a v1 UUID.'),
            ('Local v4 generation', 'Generates v4 UUIDs with the browser crypto RNG — no backend, instant results.'),
        ],
        'steps': [
            'Paste the UUID to parse on the left (with or without hyphens).',
            'The right side shows version, variant and, for v1, the timestamp and node.',
            'Click "Generate v4" to get a new random UUID.',
        ],
        'faq': [
            ('Are UUIDs case-insensitive?', 'The letter part is case-insensitive by spec, but the standard form is lowercase; this tool ignores case when parsing.'),
            ('Are v4 UUIDs really unique?', 'v4 uses 122 random bits, making collisions negligible. This tool only parses and generates; it does not guarantee global uniqueness across devices.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Unix Timestamp and Date Converter', 'timestamp/'),
            ('Snowflake ID parser', 'snowflake/'),
            ('MongoDB ObjectId parser', 'objectid/'),
            ('Are generated UUIDs recorded?',
             'No. UUIDs are generated locally in your browser with cryptographically secure randomness. The page records nothing and sends no requests — it works offline.'),
            ('Are generated UUIDs recorded?',
             'No. UUIDs are generated locally in your browser with cryptographically secure randomness. The page records nothing and sends no requests — it works offline.'),
            ('Are generated UUIDs recorded?',
             'No. UUIDs are generated locally in your browser with cryptographically secure randomness. The page records nothing and sends no requests — it works offline.'),
        ],
    },
    'snowflake': {
        'nav': 'Snowflake',
        'title': 'Snowflake ID Decoder — Twitter/Discord Timestamp | DevTools',
        'description': (
            'Decode Snowflake IDs from Twitter, Discord and more: recover the millisecond timestamp, machine and '
            'sequence. Build a Snowflake from a time with a custom epoch. All computed locally.'
        ),
        'keywords': 'snowflake decoder,snowflake id,twitter id decoder,discord id decoder,snowflake timestamp,snowflake algorithm',
        'h1': 'Snowflake ID Decoder and Builder',
        'intro': [
            'A Snowflake is Twitter\'s 64-bit distributed ID: 41 bits of millisecond timestamp, 10 bits of machine '
            'and 12 bits of sequence. Paste one to reveal its creation time and machine/sequence fields.',
            'Pick Twitter, Discord or a custom epoch, and on the right you can also build a Snowflake from a given '
            'time — handy for "ID at a moment" boundary checks.',
        ],
        'features': [
            ('Multi-platform presets', 'Built-in Twitter (epoch 2010-11-04) and Discord (epoch 2015-01-01) presets, plus custom epoch and bit-width.'),
            ('Timestamp recovery', 'Decodes the millisecond timestamp and shows both UTC and local time.'),
            ('Reverse building', 'Given a time and machine/sequence, build a valid Snowflake for timestamp to ID range conversion.'),
        ],
        'steps': [
            'Choose Twitter, Discord or Custom in the preset.',
            'Paste the Snowflake ID on the left; the right side shows timestamp, machine and sequence.',
            'Fill time, node and sequence on the right and click "Build ID" to generate one.',
        ],
        'faq': [
            ('Why are the IDs so long?', 'A Snowflake is a 63-bit unsigned integer, typically 18-19 decimal digits; it is parsed as a string to avoid JavaScript number precision loss.'),
            ('What epoch do I enter for custom?', 'Enter your system\'s epoch in milliseconds (Twitter is 1288834974657), keeping the common 41/10/12 bit layout.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Twitter and X ID decoder', 'tid/'),
            ('UUID parser and generator', 'uuid/'),
            ('Unix Timestamp and Date Converter', 'timestamp/'),
            ('Is the Snowflake ID I parse uploaded?',
             'No. Decoding and building Snowflake IDs run entirely in your browser; the page has no code that sends your IDs anywhere. It works offline.'),
        ],
    },
    'tid': {
        'nav': 'Twitter ID',
        'title': 'Twitter/X ID Decoder — Tweet Creation Time | DevTools',
        'description': (
            'Decode any Twitter / X Snowflake ID: paste a tweet, user or DM id to recover its creation time, '
            'machine and sequence. Fully local, no X login required.'
        ),
        'keywords': 'twitter id decoder,x id decoder,tweet id time,twitter timestamp,twitter snowflake,x snowflake,tweet creation time',
        'h1': 'Twitter and X ID Decoder',
        'intro': [
            'Every X (formerly Twitter) object ID is a Snowflake. Paste one to recover its creation time, machine and sequence fields.',
            'IDs at or below 29700859247 are pre-Snowflake sequential numbers with no embedded time; the tool says so clearly.',
        ],
        'features': [
            ('Creation time', 'Recovers the UTC and local creation time of the ID, to the millisecond.'),
            ('Boundary detection', 'Recognizes pre-Snowflake sequential IDs and clearly reports "no embedded time".'),
            ('Time to ID', 'Given a time, build that moment\'s Twitter Snowflake ID for time-range lookups.'),
        ],
        'steps': [
            'Paste any tweet, user or DM numeric ID.',
            'The right side shows creation time, machine and sequence; very early IDs report no time.',
            'Enter a time on the right and click "Time to ID" to build one.',
        ],
        'faq': [
            ('Why do some IDs have no time?', 'IDs before Snowflake launched in Nov 2010 are plain sequential numbers (about <= 29700859247) and contain no time to recover.'),
            ('Does decoding need an X login?', 'No. The Snowflake timestamp is encoded in the ID itself; this tool computes locally with no X API involved.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Snowflake ID decoder', 'snowflake/'),
            ('Unix Timestamp and Date Converter', 'timestamp/'),
            ('Is the ID I parse uploaded?',
             'No. ID-to-creation-time conversion runs locally in your browser; the page has no code that sends your IDs anywhere.'),
        ],
    },
    'objectid': {
        'nav': 'ObjectId',
        'title': 'MongoDB ObjectId Parser & Generator — Timestamp | DevTools',
        'description': (
            'Parse a 24-hex MongoDB ObjectId online: recover creation time, machine, process and counter, and '
            'generate a new ObjectId. All done locally in your browser.'
        ),
        'keywords': 'objectid parser,objectid generator,mongodb id,mongodb objectid time,objectid online,objectid validate',
        'h1': 'MongoDB ObjectId Parser and Generator',
        'intro': [
            'A MongoDB ObjectId is 12 bytes: the first 4 bytes are the Unix seconds of creation. Paste one to see its timestamp and fields.',
            'Click "Generate ObjectId" for a well-formed random ObjectId to build local test data.',
        ],
        'features': [
            ('Timestamp recovery', 'From the first 4 bytes, recover the second-level creation time and show UTC and local time.'),
            ('Field breakdown', 'Shows machine, process and incrementing counter so you can trace an ID\'s origin.'),
            ('Local generation', 'One click generates a well-formed ObjectId without a MongoDB instance.'),
        ],
        'steps': [
            'Paste a 24-hex ObjectId on the left.',
            'The right side instantly shows the timestamp and fields; a format error is flagged.',
            'Click "Generate ObjectId" to get a new random ID.',
        ],
        'faq': [
            ('Is the ObjectId time accurate?', 'The first 4 bytes are the second-level Unix time of creation, precise to the second; it is client-generated and usually reflects the creation moment.'),
            ('Does the generated one match the database?', 'The structure is identical (time plus random machine/process plus counter), but machine and counter are random fill for local testing, not a real instance.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('UUID parser and generator', 'uuid/'),
            ('Unix Timestamp and Date Converter', 'timestamp/'),
            ('Is the ObjectId I parse uploaded?',
             'No. Decoding and generating ObjectIds run entirely in your browser; the page has no code that sends your IDs anywhere. It works offline.'),
        ],
    },
    'firebase': {
        'nav': 'Firebase ID',
        'title': 'Firebase Push ID Parser & Generator — Timestamp | DevTools',
        'description': (
            'Decode a 20-char Firebase Push ID\'s creation timestamp, or generate a valid ID from the current or a '
            'chosen time. Fully local, no data uploaded.'
        ),
        'keywords': 'firebase id parser,firebase push id,push id decoder,firebase timestamp,firebase id generator,firebase id online',
        'h1': 'Firebase Push ID Parser and Generator',
        'intro': [
            'A Firebase Realtime Database Push ID is 20 chars: the first 8 encode the creation millisecond timestamp '
            'in base-64, the last 12 are random. Paste one to recover its creation time.',
            'Click "Generate (now)" or generate from a chosen time to get a valid Push ID for test data.',
        ],
        'features': [
            ('Timestamp recovery', 'From the first 8 chars recover the millisecond creation timestamp and show UTC and local time.'),
            ('Time-based generation', 'Generate valid Push IDs from the current time or any chosen time for range comparison.'),
            ('Local compute', 'No Firebase API is called; parsing and generation are fully local.'),
        ],
        'steps': [
            'Paste a 20-char Firebase Push ID on the left.',
            'The right side instantly shows the creation time and random suffix; a format error is flagged.',
            'Click "Generate (now)" or enter a time and "Generate at time" to get a new ID.',
        ],
        'faq': [
            ('Why are the first 8 chars the time?', 'Firebase encodes the timestamp in base-64 with the most significant digit first, so the IDs also sort chronologically by dictionary order.'),
            ('Can the generated ID be written to the database?', 'The structure is valid, but the suffix is random and meant for local testing, not a real write order.'),
            ('Is the Push ID I parse uploaded?',
             'No. Push-ID-to-time conversion runs locally in your browser; the page has no code that sends your IDs anywhere.'),
        ],
        'seealso': [
            ('UUID parser and generator', 'uuid/'),
            ('Unix Timestamp and Date Converter', 'timestamp/'),
        ],
    },
    'base': {
        'nav': 'Base Converter',
        'title': 'Base Converter — Binary/Octal/Decimal/Hex (2-36) | DevTools',
        'description': (
            'Free online base converter: convert between binary, octal, decimal, hex and any base 2-36. '
            'Arbitrary precision for big numbers, 0x/0b/0o prefixes and auto-detect, all bases at a glance. Fully local.'
        ),
        'keywords': 'base converter,radix converter,binary to decimal,decimal to binary,decimal to hex,hex to decimal,arbitrary base converter,big number converter',
        'h1': 'Any-Base Converter',
        'intro': [
            'Convert a number between binary, octal, decimal, hex and any base from 2 to 36, with every base shown at once on the right.',
            'It uses big-integer math, so even very long numbers keep full precision; input may carry 0x / 0b / 0o prefixes, and "Auto-detect" infers the source base from the prefix and characters.',
        ],
        'features': [
            ('Any base 2-36', 'Pick any source and target base from 2 to 36, covering binary, octal, decimal, hex and base32/base36.'),
            ('All bases at once', 'The table on the right lists the value in every base from 2 to 36, no repeated switching.'),
            ('Big-number safe', 'Big-integer arithmetic throughout: numbers beyond 2^53 convert exactly, no float error.'),
            ('Prefixes and auto-detect', 'Accepts 0x / 0b / 0o prefixes, case-insensitive; Auto-detect infers the base from the prefix and characters.'),
        ],
        'steps': [
            'Enter a value on the left (e.g. 255, 0xFF, 0b1010, 1f).',
            'Choose the source base (leave Auto-detect if unsure) and the target base.',
            'The converted value shows on the left; every base 2-36 is listed on the right.',
        ],
        'faq': [
            ('Why is big-number conversion exact?', 'Plain math uses floats and loses precision past 2^53; here every digit is processed with big-integer arithmetic, so the result is exact.'),
            ('How does Auto-detect decide the base?', '0x means hex, 0b binary, 0o octal; all-digit input is decimal; input with a-f but no prefix is treated as hex.'),
            ('Are fractions supported?', 'Only integers for now; fractional base conversion is error-prone and rarely needed.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Binary Converter', 'binary/'),
            ('Hexadecimal Converter', 'hex/'),
            ('Text and Hex encoder', 'encode/'),
            ('Hex to RGB color', 'color/'),
            ('Are the numbers I convert uploaded?',
             'No. Any-base parsing and conversion run locally in your browser; the page has no code that sends your numbers anywhere. It works offline.'),
        ],
    },
    'binary': {
        'nav': 'Binary Converter',
        'title': 'Binary Converter - binary to decimal/hex/octal | DevTools',
        'description': (
            'Online binary converter: convert binary to decimal, hex and octal and back, grouped by 4 or 8 bits, '
            'arbitrary precision. Accepts 0b prefixes and spaced binary strings. Fully local.'
        ),
        'keywords': 'binary converter,binary to decimal,decimal to binary,binary to hex,binary grouping,bits to bytes',
        'h1': 'Binary Converter',
        'intro': [
            'Convert a binary number to decimal, hex and octal and back, with grouping by 4 bits (nibble) and 8 bits (byte) for easy checking.',
            'Accepts 0b prefixes and space/underscore grouping, with big-integer math so long binary strings stay exact.',
        ],
        'features': [
            ('Binary, decimal, hex and octal', 'Shows decimal, hex and octal results plus the bit length in one pass.'),
            ('Grouped view', 'Groups by 4 and 8 bits so long strings are readable and easy to verify byte by byte.'),
            ('Big-number safe', 'Big-integer arithmetic; binary strings beyond 2^53 convert exactly.'),
        ],
        'steps': [
            'Enter a binary number on the left (e.g. 1010, 0b11111111, 1111 0000).',
            'The right side instantly shows decimal, hex, octal and bit length.',
            'The "Grouped view" panel gives 4-bit and 8-bit groupings.',
        ],
        'faq': [
            ('Why is my binary flagged invalid?', 'Binary uses only 0 and 1; any 2-9 or letter is invalid. For other bases use the Any-Base Converter.'),
            ('How do I convert text to binary?', 'That is text encoding - use the Hex view in the Encode tool; this tool focuses on numeric base conversion.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Any-Base Converter', 'base/'),
            ('Hexadecimal Converter', 'hex/'),
            ('Text and Hex encoder', 'encode/'),
            ('Are the numbers I convert uploaded?',
             'No. Binary/decimal conversion runs locally in your browser; the page has no code that sends your numbers anywhere.'),
        ],
    },
    'hex': {
        'nav': 'Hex Converter',
        'title': 'Hex Converter — Hex to Decimal/Binary/Octal | DevTools',
        'description': (
            'Online hex converter: convert hex to decimal, binary and octal and back, with byte count and every base 2-36, '
            'arbitrary precision. Accepts 0x prefixes and upper/lower case. Fully local.'
        ),
        'keywords': 'hex converter,hex to decimal,decimal to hex,hex to binary,hexadecimal converter,hex bytes',
        'h1': 'Hexadecimal Converter',
        'intro': [
            'Convert a hex number to decimal, binary and octal and back; when the length is even it shows the byte count, and the right lists every base 2-36.',
            'Accepts 0x prefixes and upper/lower case, with big-integer math for exact conversion of long hex strings. For text-to-hex byte encoding use the Encode tool.',
        ],
        'features': [
            ('Hex, decimal, binary and octal', 'Shows decimal, binary (grouped by 4) and octal in one pass.'),
            ('Byte count', 'Shows the byte count when the length is even, so you can tell whole bytes.'),
            ('Every base at a glance', 'The right panel lists the value in every base 2-36.'),
        ],
        'steps': [
            'Enter a hex number on the left (e.g. FF, 0xFF, 1A2B, deadbeef).',
            'The right side instantly shows decimal, binary, octal and byte count.',
            'The "every base" panel lists bases 2-36.',
        ],
        'faq': [
            ('How is this different from Hex in the Encode tool?', 'Here hex is treated as a number for base conversion; the Encode tool turns text into hex byte strings - different purposes.'),
            ('Why are upper and lower case both fine?', 'Hex digits a-f are case-insensitive, so the tool accepts either.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Any-Base Converter', 'base/'),
            ('Binary Converter', 'binary/'),
            ('Text and Hex encoder', 'encode/'),
            ('Hex to RGB color', 'color/'),
            ('Is the hex I convert uploaded?',
             'No. Hex to decimal/binary conversion runs locally in your browser; the page has no code that sends your values anywhere.'),
        ],
    },
    'snippets': {
        'nav': 'Code Snippets',
        'title': 'Code Snippets — Go/Python/JS/SQL/Git | DevTools',
        'description': (
            'A library of common code snippets in six languages - Go, Python, JavaScript, Shell, SQL and Git - '
            '46 copy-ready snippets covering env vars, HTTP timeouts, concurrent error collection, debounce and '
            'retry, deep pagination, window functions, upsert, recursive queries and git rescue. Bilingual, fully local.'
        ),
        'keywords': (
            'code snippets,common code snippets,code snippet library,go snippets,python snippets,'
            'javascript snippets,shell script snippets,common sql queries,common git commands,copy paste code'
        ),
        'h1': 'Common Code Snippets',
        'intro': [
            'The snippets you reach for again and again, in six groups: Go, Python, JavaScript, Shell, SQL and Git - '
            '46 in total. Each one is the smallest complete answer to a concrete problem, not a syntax gallery.',
            'Every code block has a copy button in its top-right corner; language tabs filter the list and the '
            'search box matches titles, descriptions and code. All content is baked into the page at build time, '
            'so it stays fully readable with JavaScript disabled.',
        ],
        'features': [
            ('Six languages, 46 snippets', 'Go, Python, JavaScript, Shell, SQL and Git - env vars, HTTP timeouts, concurrent error collection, debounce and retry, deep pagination, window functions, upsert, recursive queries, git rescue and more.'),
            ('One-click copy', 'A copy button sits in the top-right of every code block; one click puts it on your clipboard.'),
            ('Language tabs + full-text search', 'Filter to one language with the tabs; the search box matches titles, descriptions and code at once.'),
            ('Readable without JS', 'Every snippet is baked into the HTML at build time, so it stays fully visible with JavaScript disabled or for crawlers that never run scripts.'),
            ('English code comments', 'All code comments are in English, so snippets drop straight into any project without half-translated remarks.'),
            ('Local and private', 'A plain static page: no login, no ads, no tracking of anything you type.'),
        ],
        'steps': [
            'Click a language tab (Go / Python / JavaScript / Shell / SQL / Git) to filter to that group.',
            'Or type a keyword such as timeout, dedupe, pagination or rebase into the search box to filter instantly.',
            'Click the Copy button in the top-right of a code block, paste it into your project and adjust as needed.',
            'To format what you pasted, use the code formatter; for Go commands see the Go cheatsheet.',
        ],
        'faq': [
            ('Can I use these snippets in production?',
             'Yes. They apply standard-library or idiomatic techniques, depend on no particular framework and carry '
             'no license restrictions - copy them and adjust the naming to taste. Still run them against your own '
             'edge cases first: a snippet solves a common problem, it does not replace your tests.'),
            ('Why are the code comments in English?',
             'This page ships in Chinese and English. Chinese comments would mean maintaining two copies of every '
             'snippet, and any missed edit shows readers a half-translated mess; English comments avoid that at the '
             'source and work in projects of either language.'),
            ('Will more languages be added?',
             'Yes. Rust, Java, C# and Kotlin are on the list, prioritised by what readers of this site actually use. '
             'You can nominate a language or a specific snippet via the feedback button.'),
            ('How often are snippets updated?',
             'The page header shows the last update. Entries affected by a new language release (Go, Python, ...) '
             'are revised afterwards, and better approaches are folded in as they are found.'),
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs locally in your browser, so your input is never sent to any server. Apart from the footer traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site collects nothing about your visit.'),
        ],
        'seealso': [
            ('Go toolchain cheatsheet', 'go-cheatsheet/'),
            ('Code formatter (HTML / CSS / JS / SQL)', 'formatter/'),
            ('JSON formatter & validator', './'),
            ('Any-Base Converter', 'base/'),
            ('Does using the snippet library record my actions?',
             'No. Snippets are baked into the page at build time, and copying only writes to your clipboard — the page records no copy actions and sends no requests.'),
            ('Does using the snippet library record my actions?',
             'No. Snippets are baked into the page at build time, and copying only writes to your clipboard — the page records no copy actions and sends no requests.'),
            ('Does using the snippet library record my actions?',
             'No. Snippets are baked into the page at build time, and copying only writes to your clipboard — the page records no copy actions and sends no requests.'),
        ],
    },
    'sql-formatter': {
        'nav': 'SQL Formatter',
        'title': 'SQL Formatter Online — Pretty-Print SQL Free | DevTools',
        'description': (
            'Free online SQL formatter: line breaks, indentation and keyword casing for SELECT, '
            'multi-table JOIN, subqueries, INSERT, UPDATE and CREATE TABLE. Indent width 2 or 4 spaces, '
            'optional keyword uppercasing, everything runs locally in your browser.'
        ),
        'keywords': (
            'sql formatter,online sql formatter,sql beautifier,sql format online,'
            'sql keyword uppercase,sql pretty print,format sql query'
        ),
        'h1': 'SQL Formatter Online',
        'intro': [
            'One-line SQL is hard to review. This tool restores its structure: every major clause on its '
            'own line, field lists and conditions one per line, JOIN / ON / AND indented by level, and '
            'keywords uppercased — subqueries, INSERT, UPDATE and CREATE TABLE follow the same rules.',
            'Indent width (2 or 4 spaces) and keyword casing are both optional, and the output only '
            'changes layout, never meaning. Everything runs locally in your browser; your SQL never '
            'leaves the page.',
        ],
        'features': [
            ('Clause-level breaks', 'SELECT, FROM, WHERE, GROUP BY, ORDER BY, HAVING, LIMIT and friends each get their own line.'),
            ('Condition & JOIN indent', 'AND / OR / ON nest by level, so multi-table joins and subqueries read cleanly.'),
            ('Optional casing', 'Uppercase keywords or keep the original spelling; identifiers and string literals are never touched.'),
            ('Indent width', 'Switch between 2 and 4 spaces to match your team style guide.'),
            ('Multi-statement ready', 'A whole script is split on semicolons and each statement is formatted on its own.'),
            ('Runs locally', 'Parsing and layout happen in the browser — no upload, no server round-trip.'),
        ],
        'steps': [
            'Paste the SQL you want formatted into the left panel — one statement or a whole script.',
            'Adjust the "大写" (uppercase) and Indent options if needed.',
            'Hit 格式化 (Format) and read the result on the right.',
            'Copy or download the result and paste it back into your database client.',
        ],
        'faq': [
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs '
             'locally in your browser, so your input is never sent to any server. Apart from the footer '
             'traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site '
             'collects nothing about your visit.'),
            ('Does formatting change the meaning of my SQL?',
             'No. Only whitespace and line breaks change: keyword casing, indentation and clause breaks. '
             'String literals, comments and identifiers are preserved exactly as written.'),
            ('Which SQL dialects are supported?',
             'The layout rules target common SQL and cover the usual MySQL, PostgreSQL, SQLite and SQL '
             'Server syntax: multi-word keywords (GROUP BY, LEFT OUTER JOIN), qualified names '
             '(schema.table) and all three quote styles are recognised.'),
            ('Why did my comments move?',
             'Line comments (-- and #) and block comments (/* */) are kept verbatim as their own tokens, '
             'but the line they sit on is re-indented with the surrounding clause. Comment text itself '
             'is never modified.'),
            ('Why does the comma inside a function not break the line?',
             'Commas inside parentheses are treated as function arguments and stay inline (count(a, b)); '
             'only top-level lists such as the SELECT list or GROUP BY break one item per line, so '
             'function calls are never torn apart.'),
        ],
        'seealso': [
            ('Code formatter (HTML / CSS / JS / SQL)', 'formatter/'),
            ('CSV to SQL INSERT generator', 'csv-to-sql-insert/'),
            ('JSON and CSV converter', 'json/'),
            ('Go toolchain cheatsheet', 'go-cheatsheet/'),
            ('Code snippets (Go / Python / JS / SQL / Git)', 'snippets/'),
        ],
    },
    'markdown-to-html': {
        'nav': 'MD to HTML',
        'title': 'Markdown to HTML — Online MD Converter | DevTools',
        'description': (
            'Convert Markdown to HTML online: headings, ordered and unordered lists, tables, fenced code '
            'blocks, quotes, links and images all render to clean semantic HTML. Copy the fragment or '
            'download a full page — everything runs locally in your browser.'
        ),
        'keywords': (
            'markdown to html,online markdown converter,md to html,markdown converter,'
            'markdown preview,markdown html,convert markdown'
        ),
        'h1': 'Markdown to HTML Converter',
        'intro': [
            'Turn Markdown into clean semantic HTML in real time: heading levels, lists, tables, fenced '
            'code blocks, block quotes, horizontal rules and inline bold, italic, strikethrough, code, '
            'links and images all get their proper tags. Toggle 预览 (preview) to see the rendered page.',
            'All text is HTML-escaped before the Markdown rules run, and link or image URLs are '
            'scheme-checked — pasted HTML or javascript: links cannot escape into executable markup. '
            'Conversion happens entirely in the browser; your Markdown is never sent anywhere.',
        ],
        'features': [
            ('Full block syntax', 'Headings, lists (one nesting level), tables, code fences, quotes, rules and paragraphs.'),
            ('Complete inline set', 'Bold, italic, strikethrough, inline code, links and images; code content is never re-parsed.'),
            ('XSS-safe', 'Text is escaped first and javascript: / data: URLs are rejected, so nothing executes.'),
            ('Table alignment', 'Left, right and centre column alignment in Markdown tables.'),
            ('Fragment or page', 'Copy just the HTML fragment, or download a complete .html file with DOCTYPE and viewport.'),
            ('Runs locally', 'No backend call at all — works offline once the page has loaded.'),
        ],
        'steps': [
            'Paste Markdown into the left panel; the 示例 (sample) button loads a full demo.',
            'Hit 转换 (Convert) and read the result on the right as preview or source.',
            'Copy the HTML fragment, or download it as a complete web page file.',
        ],
        'faq': [
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs '
             'locally in your browser, so your input is never sent to any server. Apart from the footer '
             'traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site '
             'collects nothing about your visit.'),
            ('Can I use the output on a production page?',
             'Yes. The output is standard semantic HTML (h1-h6, p, ul/ol/li, table, pre/code, '
             'blockquote) and carries no styling of its own; the download option even wraps it in a '
             'full document with DOCTYPE and viewport.'),
            ('Are GFM strikethrough and tables supported?',
             'Yes. ~~strikethrough~~, | tables | and ``` fenced code are all supported. Task lists '
             '(- [ ]) are not, and render as plain list items.'),
            ('Why did the HTML tags I pasted disappear?',
             'For safety every text run is HTML-escaped first, so <div> shows up as &lt;div&gt; instead '
             'of becoming a real tag. This is deliberate: the tool converts Markdown syntax to HTML, '
             'it does not execute the HTML you paste.'),
            ('Is Markdown syntax inside code blocks processed?',
             'No. Fenced code blocks and inline code are escaped as plain text, so ** and [link] '
             'inside them display literally instead of being rendered.'),
        ],
        'seealso': [
            ('Code formatter (HTML / CSS / JS / SQL)', 'formatter/'),
            ('JSON and YAML converter', 'yaml/'),
            ('JSON and TOML converter', 'toml/'),
            ('JSON and CSV converter', 'json/'),
            ('Code snippets (Go / Python / JS / SQL / Git)', 'snippets/'),
        ],
    },
    'gofmt-online': {
        'path': 'gofmt-online/',
        'nav': 'Go Formatter',
        'title': 'Go Formatter Online — Free gofmt, Runs In-Browser | DevTools',
        'description': (
            'Format Go code online with real gofmt rules — a WebAssembly build of Go\'s official '
            'go/format package running entirely in your browser. Nothing is uploaded. '
            'Copy or download the .go file, with line:column errors for syntax problems.'
        ),
        'keywords': (
            'gofmt online,go formatter,format go code,gofmt tool,go beautifier,'
            'golang formatter,go code formatter,goimports alternative'
        ),
        'h1': 'Go Formatter Online (gofmt)',
        'intro': [
            'Paste Go source code, hit Format, and get exactly what gofmt produces: tab '
            'indentation, aligned operators, grouped imports and struct fields lined up by the '
            'longest name. The rules come from real gofmt, not a regex approximation.',
            'The formatting engine is Go\'s official go/format package compiled to WebAssembly, '
            'so every calculation happens in your browser and your code is never sent anywhere. '
            'That is the difference from most "online formatters" — it keeps working offline, '
            'and pasting company code carries no leak risk.',
        ],
        'features': [
            ('Real gofmt rules', 'The engine is Go\'s official go/format package compiled to WebAssembly with TinyGo. Output is byte-for-byte identical to the command-line gofmt, tabs and alignment included.'),
            ('Runs in your browser', 'The 268 KB wasm engine is self-hosted and warms up in the background after page load. Formatting is fully local — your code never leaves your device.'),
            ('Syntax error positions', 'Invalid code produces Go-compiler-style messages with line:column and a reason, pointing straight at the problem.'),
            ('Copy or download', 'Copy the result in one click or download it as a .go file. Code that is already gofmt-formatted comes back unchanged.'),
            ('No sign-up, no ads', 'Open the page and use it. No accounts, no queues, no limits, no ads or pop-ups.'),
            ('Go resources included', 'The site also has a Go toolchain cheatsheet, a deep dive on gofmt vs goimports, and copy-ready Go snippets to go with this tool.'),
        ],
        'steps': [
            'Paste Go source code into the left editor, or click "Example" to load an unformatted demo.',
            'Click "Format" — the gofmt output appears on the right immediately.',
            'Click "Copy" to put the result on your clipboard, or "Download" to save it as a .go file.',
            'If a syntax error is reported, fix the line:column it points to and format again.',
        ],
        'faq': [
            ('Is my code uploaded to a server?',
             'No. The formatting engine is Go compiled to WebAssembly and runs in your browser; '
             'the page contains no code that sends your source anywhere. You can disconnect from '
             'the network and keep using this page (the first load needs the network to fetch the '
             'wasm engine file).'),
            ('Is the output identical to the command-line gofmt?',
             'Yes. The engine is Go\'s official go/format package and applies the same rules as '
             'go fmt. The only difference is that the CLI version reads and writes files, while '
             'this tool works on pasted text.'),
            ('Why are there no options for indent width or quote style?',
             'Because gofmt\'s design philosophy is "no configuration" — every Go codebase in the '
             'world looks the same, and that is precisely its value over other languages\' '
             'formatters. This tool deliberately offers no knobs either.'),
            ('Does it organise imports like goimports?',
             'No. goimports adds and removes imports based on dependency information, which '
             'cannot be fully done in a pure front end. This tool only formats, exactly like '
             'gofmt. Read the site blog post "gofmt vs goimports" for the difference.'),
            ('How large a file can it handle?',
             'Files of a few hundred KB are no problem (a 3000-line file formats in about 130 ms '
             'in testing). For anything larger, use the command-line gofmt — the editor input '
             'experience reaches its limits first anyway.'),
        ],
        'seealso': [
            ('Code formatter (HTML / CSS / JS / SQL)', 'formatter/'),
            ('Blog: gofmt vs goimports and CI practice', 'blog/gofmt-vs-goimports/'),
            ('Go toolchain cheatsheet', 'go-cheatsheet/'),
            ('Code snippets (Go / Python / JS / SQL / Git)', 'snippets/'),
            ('JSON formatter & validator', './'),
        ],
    },
    'cron-generator': {
        'path': 'cron-generator/',
        'nav': 'Cron Generator',
        'title': 'Cron Expression Generator — Visual Builder | DevTools',
        'description': (
            'Generate cron expressions online: pick values for the five cron fields '
            '(minute, hour, day, month, weekday) and get a standard 5-field crontab '
            'expression instantly, with built-in */n steps on every field and optional '
            'start values for start/step forms like 5/2. Copy or download it. '
            'Runs entirely in your browser.'
        ),
        'keywords': (
            'cron expression generator,cron generator,crontab generator,linux cron job,'
            'cron expression builder,crontab expression,schedule expression,'
            'cron every n minutes,cron start step'
        ),
        'h1': 'Cron Expression Generator',
        'intro': [
            'The five crontab fields (minute, hour, day, month, weekday) are easy to remember '
            'and easy to get wrong: one extra space, a weekday of 8, or */5 typed as 5, and '
            'the job fires at a strange time. This generator turns the five fields into '
            'dropdowns — pick, and the standard expression is assembled for you.',
            'Every field accepts "every", a specific value or a */n step, and picking a step '
            'reveals a start input — minute */2 with start 5 yields 5/2, every 2 minutes '
            'from minute 5, keeping the job off the congested top of the hour. '
            'Everything runs locally in your browser; nothing is sent anywhere.',
        ],
        'features': [
            ('Five visual fields', 'Pick minute / hour / day / month / weekday in order and get a standard 5-field cron expression, with no risk of mistyping a field.'),
            ('Steps and common values built in', 'All five fields include */n steps (minute up to */30, month also */3, */4 and */6); hour, day, month and weekday offer every common value, with weekdays shown as 0-7 plus the weekday abbreviation.'),
            ('Custom start with start/step', 'Pick any step and the adjacent start input rewrites */2 into 5/2 (every 2 minutes from minute 5), shifting jobs off the top of the hour; leave it empty or at the field minimum to keep the canonical */2.'),
            ('Live regeneration', 'Once an expression exists, changing any field regenerates it immediately — no button pressing required.'),
            ('Copy or download', 'Copy the expression to your clipboard or download it as crontab.txt, ready to paste into crontab -e.'),
            ('Local and dependency-free', 'The page is static HTML with no backend calls; the generation logic is built in and works offline.'),
            ('Real-world ready', 'Output works as-is in Linux crontab, in-container cron for Docker, and in the schedule field of GitHub Actions.'),
        ],
        'steps': [
            'Select values for minute, hour, day, month and weekday on the left (all default to *, i.e. every unit); when you pick a */n step, the start input next to it offsets it — minute */2 with start 5 gives 5/2.',
            'Click "Generate" — the assembled cron expression appears on the right.',
            'Click "Copy" or "Download" and paste the expression into crontab -e or your CI config.',
            'Changing any field regenerates instantly; "Clear" resets everything to the defaults.',
        ],
        'faq': [
            ('How do I run a job every 2 minutes starting at minute 5?',
             'Pick */2 (every 2 minutes) for minute and type 5 into the start input that '
             'appears; the expression becomes 5/2 * * * * — firing at minutes 5, 7, 9 … 59. '
             'Leaving start empty or at 0 keeps the canonical */2. Note that start/step is '
             'a cronie extension; on older systems write the equivalent 5-59/2.'),
            ('Can I use the expression right away?',
             'Yes. The output is a standard 5-field crontab expression (minute hour day month '
             'weekday), identical in format to crontab -e, in-container Docker cron and CI '
             'schedule fields — paste and run.'),
            ('Do 0 and 7 both mean Sunday?',
             'Yes. In the crontab spec both 0 and 7 represent Sunday, so this tool offers both; '
             'for weekdays use 1-5, and for weekends 6 (Saturday) or 0/7 (Sunday).'),
            ('Why is there no "next run time" preview?',
             'Generating an expression and explaining one are two different jobs; this page '
             'focuses on the former — turning visual picks into an expression. Explaining an '
             'existing expression (with next-run computation) belongs on a separate page, so '
             'neither has to carry two sets of logic.'),
            ('Are seconds or a year field supported?',
             'No. Standard crontab has five fields and no seconds; the 6/7-field Spring format '
             'and the 7-field Quartz format mean different things per field, and mixing them '
             'up causes mistakes. Configure those per their own framework documentation.'),
            ('Is my input uploaded?',
             'No. This page makes no backend calls at all; all fields and expressions are '
             'handled in the browser and the page works offline.'),
        ],
        'seealso': [
            ('Unix timestamp converter', 'timestamp/'),
            ('Batch timestamp converter', 'batch/'),
            ('Common timestamp lookup (today / this week / this month)', 'timestamp-list/'),
            ('CSV to SQL INSERT generator', 'csv-to-sql-insert/'),
            ('JSON formatter & validator', './'),
        ],
    },
    'csv-to-sql-insert': {
        'path': 'csv-to-sql-insert/',
        'nav': 'CSV to SQL',
        'title': 'CSV to SQL INSERT Generator — Bulk INSERTs | DevTools',
        'description': (
            'Convert CSV to SQL INSERT statements online: the first row becomes the column '
            'list, empty cells become NULL, single quotes are escaped by doubling, and quoted '
            'commas are parsed correctly. Bulk-generate executable INSERT statements — all '
            'in your browser, nothing uploaded.'
        ),
        'keywords': (
            'csv to sql,csv to insert,csv to sql insert,sql insert generator,'
            'import csv to sql,bulk insert generator,csv to database'
        ),
        'h1': 'CSV to SQL INSERT Generator',
        'intro': [
            'The fastest way to load a CSV into a database is a single INSERT statement with '
            'many VALUES tuples. Paste your CSV, set the table name, and get executable SQL '
            'immediately: the first row becomes the column list, empty cells become NULL, '
            'single quotes are doubled per the SQL standard, and quoted comma fields are '
            'split correctly.',
            'The conversion runs entirely in your browser and your CSV is never sent to a '
            'server — for export files with sensitive data, that matters more than "online" itself.',
        ],
        'features': [
            ('First row is the header', 'The CSV header row is detected automatically and becomes the column list — no separate column input needed.'),
            ('Standard SQL escaping', 'Single quotes are doubled (O\'Neil → \'O\'\'Neil\'), empty values become NULL, numbers stay unquoted and strings are quoted.'),
            ('Quoted field support', 'Parsing follows RFC 4180: "a,b" stays one field, and embedded commas and escaped quotes ("") are handled.'),
            ('Custom table name', 'Set the table name; identifiers are wrapped in backticks (MySQL style) so reserved words do not break the statement.'),
            ('Bulk multi-row output', 'All data rows become multiple VALUES tuples in one INSERT statement — efficient to execute.'),
            ('Fully local', 'No backend API; the CSV never leaves the browser. Copy the SQL or download it as a .sql file.'),
        ],
        'steps': [
            'Paste CSV content into the left panel — the first line must be the header (column names).',
            'Fill in the table name (defaults to my_table).',
            'Click "Generate" — the INSERT statement appears on the right.',
            'Click "Copy" or "Download", and check column names and table structure before executing.',
        ],
        'faq': [
            ('Is my CSV data uploaded?',
             'No. Parsing and generation are done by JavaScript in the page; there is no code '
             'that sends your CSV anywhere, and the page works offline (the first load needs '
             'the network for page resources).'),
            ('Which database dialect is the output?',
             'MySQL / MariaDB style: backticked identifiers, single-quoted strings, doubled '
             'quote escaping. PostgreSQL and SQLite mostly accept it too; for SQL Server '
             'change the backticks to square brackets — NULL and escaping rules are the same.'),
            ('What if the first row is not a header?',
             'The first row is always treated as the header for now. If your data has none, '
             'add a column-name line (e.g. c1,c2,c3) at the top before generating, then rename '
             'the columns to the real ones before executing.'),
            ('Do commas and newlines inside fields break it?',
             'No. Parsing follows the quoting rules: a field like "a,b" stays intact, and '
             'embedded commas and escaped quotes ("") are handled correctly.'),
            ('Can I execute the output directly?',
             'The statement is a standard INSERT, but confirm the table exists, the column '
             'names and data types match, and the row count fits your transaction budget — '
             'this tool only generates SQL and makes no assumptions about your schema.'),
        ],
        'seealso': [
            ('CSV viewer & converter', 'csv/'),
            ('JSON ↔ CSV converter (JSON toolbox)', './'),
            ('Cron expression generator', 'cron-generator/'),
            ('Code formatter (HTML / CSS / JS / SQL)', 'formatter/'),
            ('Code snippets (Go / Python / JS / SQL / Git)', 'snippets/'),
        ],
    },
}

# Inner HTML of <section class="seo-content legal">...</section>, in English.
# Same headings/structure as the Chinese version (h2 + p + ul/ol), translated.
PRIVACY_BODY_EN = """
<h1>Privacy Policy</h1>
<p class="legal-updated">Last updated: September 10, 2026</p>

<h2>1. Data You Enter Into the Tools</h2>
<p>
  Every developer tool on this site (JSON formatting and validation, text diffing, encoding and
  decoding, regex testing, timestamp conversion, hashing, code formatting, string processing and the
  generators) parses, converts and computes entirely in your browser with JavaScript.
  The text, code and files you enter or paste into these tools <strong>are not sent to this site's
  servers, and this site has no server-side endpoint that receives them</strong>.
</p>
<p>
  Features that involve files (file hashing, image-to-Base64) use the browser's local file reading
  APIs, and the file contents likewise never leave your device.
</p>

<h2>2. Visit Analytics</h2>
<p>This site uses two third-party analytics services to understand traffic, referrers and which tools are used:</p>
<ul>
  <li>
    <strong>busuanzi</strong> (busuanzi.ibruce.info) — counts page views and visitors for the counter
    shown in the footer. When a page loads, it receives your browser identifier (User-Agent), the
    referring page URL and an approximate geographic location derived from your IP address, which it
    uses to distinguish visitors and de-duplicate the count.
  </li>
  <li>
    <strong>Baidu Analytics</strong> (hm.baidu.com) — analyses traffic sources, geographic
    distribution, devices and how popular each tool page is. It <strong>sets cookies in your
    browser</strong> (for example <code>HMACCOUNT</code>, <code>Hm_lvt_*</code>,
    <code>Hm_lpvt_*</code>) to recognise returning visitors, and collects your IP address, browser
    and operating system details, the referring page and your navigation path across this site.
  </li>
</ul>
<p>
  This site has no user accounts and does not collect personal information such as names, email
  addresses or phone numbers. If you would rather not be counted, you can block
  <code>hm.baidu.com</code> and <code>busuanzi.ibruce.info</code> in your browser or with an
  extension — every tool keeps working normally.
</p>

<h2>3. Third-Party Resources</h2>
<p>To keep the pages lightweight, this site loads the following third-party resources from public CDNs. Your browser communicates with those services when they load, and their own privacy policies apply:</p>
<ul>
  <li><strong>cdn.jsdelivr.net</strong> — provides the YAML / TOML conversion libraries, loaded on demand (only on the relevant tool pages).</li>
  <li><strong>busuanzi.ibruce.info</strong> — the visit counter in the footer.</li>
  <li><strong>hm.baidu.com</strong> — Baidu Analytics, used for site statistics.</li>
</ul>
<p>
  The code editor (CodeMirror) and the QR code generation library used to come from
  <code>cdnjs.cloudflare.com</code>. They are now served from <code>/assets/cdn/</code> under this
  site's own domain, so loading them no longer involves any communication with Cloudflare.
</p>
<p>
  No third-party domains beyond these three are requested. If you work in a privacy-sensitive
  environment you can block them; apart from the visit counter and the editor's syntax highlighting,
  every tool keeps working, because all computation happens locally and does not depend on these
  external resources.
</p>

<h2>4. Advertising</h2>
<p>
  This site may display advertising in the future to cover running costs. If that happens, ad
  providers may use cookies or similar technologies to serve ads, and this policy will be updated at
  the same time to name those providers and describe how they use data. This site currently
  <strong>displays no advertising</strong>.
</p>

<h2>5. Cookies and Local Storage</h2>
<p><strong>This site sets no cookies of its own.</strong> The only cookies come from Baidu Analytics,
described above, and are used to distinguish unique visitors and recognise returning ones. You can
clear or block them at any time in your browser.</p>
<p>
  The site also uses browser localStorage to remember two preferences. They stay on your device, are
  never synced to any server, and are removed when you clear your browser data:
</p>
<ul>
  <li>theme preference (light or dark);</li>
  <li>language preference (Chinese or English), so a manual choice is remembered and you are not
      redirected on every visit.</li>
</ul>

<h2>6. Changes to This Policy</h2>
<p>
  If this policy changes, the "Last updated" date at the top of this page will be revised. Continuing
  to use this site means you accept the updated policy.
</p>

<h2>7. Contact</h2>
<ul>
  <li>Open an <a href="https://github.com/xwjiang2003/tools/issues" rel="noopener">issue</a> in the project repository, or start a thread in <a href="https://github.com/xwjiang2003/tools/discussions" rel="noopener">Discussions</a>;</li>
  <li>Or email <a href="mailto:278975598@qq.com?subject=%5BDevTools%5D%20Privacy">278975598@qq.com</a>.</li>
</ul>
"""
