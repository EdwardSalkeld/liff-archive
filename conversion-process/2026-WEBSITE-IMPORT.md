# 2026 website import

The 152 film and programme pages in `hugo/content/films/2026/` were extracted from the LIFF website HTML cached by `liff-utils` on 14 October 2026. Each page retains its original LIFF URL in `source-url` front matter. No raw HTML is committed here.

The site's film metadata supplies director, runtime, production year, country, language, distributor, certificate, and premiere status where published. The archive uses its existing broad strand names; Day of the Dead and Night of the Dead films keep their own strands. Descriptions, quotations, content guidance, and the named shorts within programme tables are rendered as Markdown.

The site had no description for **LIFF SHORTS 2026: The Award-Winners** at import time. Its archive file records that absence in an HTML comment. The seven new social events, workshops, quizzes, and the Spotlight Forum are excluded from the 2026 film list in `liff-utils`.
