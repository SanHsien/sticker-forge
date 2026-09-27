# LINE Static Sticker 3x3 Prompt

Purpose: copy this prompt into ChatGPT, Gemini, or another image generation tool to create a 3x3 sticker grid that can be imported back into `sticker-forge`.

## Fields

- Character: `{character}`
- Theme: `{theme}`
- Tone: `{tone}`
- Visual style: `{style}`
- Language: `{language}`
- Sticker text 1-8: `{text_1}` to `{text_8}`
- Action 1-8: `{action_1}` to `{action_8}`

## Text version

Generate one 3x3 grid image for LINE static sticker source art.

Specifications:

- Character: `{character}`
- Theme: `{theme}`
- Tone: `{tone}`
- Style: `{style}`
- Language: `{language}`
- Layout: 3 columns x 3 rows, 9 cells total, each cell is an independent sticker composition
- Background: solid `{chroma_key_label}` (`{chroma_key_hex}`) for later chroma-key cleanup
- Output: one square image with clear spacing between all 9 cells
- Keep the character consistent in every cell
- Use one main character per cell; avoid complex backgrounds
- Keep text short, clear, centered or close to the character, and never cropped
- Do not use `{chroma_key_avoid}` in the character, clothing, props, shadows, or highlights; use `{chroma_key_substitutions}` if the character would otherwise be too close to the background color

Grid content:

1. `{text_1}`, action: `{action_1}`
2. `{text_2}`, action: `{action_2}`
3. `{text_3}`, action: `{action_3}`
4. `{text_4}`, action: `{action_4}`
5. `{text_5}`, action: `{action_5}`
6. `{text_6}`, action: `{action_6}`
7. `{text_7}`, action: `{action_7}`
8. `{text_8}`, action: `{action_8}`
9. Blank spare cell, same character and style, no text

Avoid:

- Do not use existing IP, trademarks, brand characters, celebrities, political figures, or real-person likenesses
- Do not generate sexual, hateful, violent, scam, personal-data, or infringing content
- Do not claim this is official LINE content, certified by LINE, or guaranteed to pass review

## No-text version

Generate one 3x3 grid image for LINE static sticker source art.

Specifications:

- Character: `{character}`
- Theme: `{theme}`
- Tone: `{tone}`
- Style: `{style}`
- Layout: 3 columns x 3 rows, 9 cells total, each cell is an independent sticker composition
- Background: solid `{chroma_key_label}` (`{chroma_key_hex}`) for later chroma-key cleanup
- Output: one square image with clear spacing between all 9 cells
- Keep the character consistent in every cell
- Use one main character per cell; avoid complex backgrounds
- Do not add any text, signatures, watermarks, or logos
- Do not use `{chroma_key_avoid}` in the character, clothing, props, shadows, or highlights; use `{chroma_key_substitutions}` if the character would otherwise be too close to the background color

Grid content:

1. Action: `{action_1}`
2. Action: `{action_2}`
3. Action: `{action_3}`
4. Action: `{action_4}`
5. Action: `{action_5}`
6. Action: `{action_6}`
7. Action: `{action_7}`
8. Action: `{action_8}`
9. Blank spare cell, same character and style

Avoid:

- Do not use existing IP, trademarks, brand characters, celebrities, political figures, or real-person likenesses
- Do not generate sexual, hateful, violent, scam, personal-data, or infringing content
- Do not claim this is official LINE content, certified by LINE, or guaranteed to pass review
