# Malformed Table Test

This is a test with a table that might cause issues.

| Header 1 | Header 2 |
|----------|----------|
| Cell 1.1 | Cell 1.2 |
| Cell 2.1 | <!-- This might break the table structure for some converters if not handled well -->
| Cell 3.1 | Cell 3.2 |

This content is after the table.
