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
        'title': 'JSON Formatter & Validator Online — Free, In-Browser | DevTools',
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
        ],
    },
    'hotnews': {
        'nav': 'Tech News',
        'title': "Today's Tech News — Live Headlines for Developers | DevTools",
        'description': (
            'A tech news page rebuilt every day at 08:00 (UTC+8) from Hacker News, TechCrunch, '
            'The Verge and Ars Technica. Every headline links straight to the original article. '
            'No signup, no ads, no tracking.'
        ),
        'keywords': (
            'tech news today,daily tech headlines,hacker news front page,developer news,'
            'tech news aggregator,techcrunch headlines,ars technica,the verge tech'
        ),
        'h1': "Today's Tech News for Developers",
        'intro': [
            'One page with the day\u2019s most useful technology reading. It pulls the public RSS '
            'feeds of Hacker News, TechCrunch, The Verge and Ars Technica into a single list, keeps '
            'the source\u2019s own ordering, and links every headline straight to the original '
            'article. Nothing is republished here — the copyright stays with each publisher.',
            'The list is refreshed and the page rebuilt once a day at 08:00 (UTC+8). Because the '
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
            ('Updated daily at 08:00',
             'A scheduled job refetches every source and rebuilds the page each morning, so what '
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
             'Once a day at 08:00 UTC+8. The scheduled job refetches every source and rebuilds the '
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
  <li><strong>cdnjs.cloudflare.com</strong> — provides the CodeMirror code editor and the QR code generation library.</li>
  <li><strong>busuanzi.ibruce.info</strong> — the visit counter in the footer.</li>
  <li><strong>hm.baidu.com</strong> — Baidu Analytics, used for site statistics.</li>
</ul>
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
