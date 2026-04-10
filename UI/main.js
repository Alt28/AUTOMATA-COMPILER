  
  let fitAddon;
  document.addEventListener('DOMContentLoaded', async () => {

  // Auto-target Flask backend when running from a different origin (e.g., VS Code Live Server on 5500)
  const API_BASE = (location.port && location.port !== '5000') ? 'http://localhost:5000' : '';

  // Use same-origin Socket.IO connection for portability (works in Docker and cloud)
  const socketBase = (location.port && location.port !== '5000') ? 'http://localhost:5000' : undefined;
  const socket = socketBase ? io(socketBase, { reconnection: true, reconnectionAttempts: Infinity, reconnectionDelay: 1000 }) : io({ reconnection: true, reconnectionAttempts: Infinity, reconnectionDelay: 1000 });
    window._galSocket = socket;  // Expose globally for inline scripts
    let waitingForInput = false;
    let userInput = '';
    // Allow inline scripts to reset input state on re-run
    window._resetInputState = function() { waitingForInput = false; userInput = ''; };
    let inputCallback = null;
    let variable = '';  // Store the variable name for which we need input
    let termInputRegistered = false;

    socket.on('connect', () => {
        console.log('Socket.IO connected, sid:', socket.id);
    });

    socket.on('disconnect', () => {
        console.log('Socket.IO disconnected');
    });
    //



      require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.43.0/min/vs',
          'xterm': 'https://cdn.jsdelivr.net/npm/xterm/lib',
          'xterm-addon-fit': 'https://cdn.jsdelivr.net/npm/xterm-addon-fit/lib/xterm-addon-fit',
          
      } });

  require(['vs/editor/editor.main'], function () {

          monaco.languages.register({ id: "gal" });

          monaco.languages.setMonarchTokensProvider("gal", {
          tokenizer: {
              
              root: [
                  // GAL basic data types
                  [/\b(tree|seed|leaf|branch|vine)\b/, "type"],
                  // GAL advanced data types
                  [/\b(variety|fertile|soil|bundle)\b/, "advancedType"],
                  // GAL control flow
                  [/\b(plant|harvest|grow|prune|graft|water|sow|root|sprout|bud|cultivate|tend|skip|reclaim|pollinate)\b/, "control"],
                  // GAL boolean values
                  [/\b(sunshine|frost|tr|fs|empty)\b/, "boolean"],
                  // GAL I/O functions
                  [/\b(bloom|wither|spring)\b/, "io"],
                  // Comments
                  [/\/\/.*/, "comment"],
                  [/#.*/, "comment"],
                  [/\/\*/, 'comment', '@comment'],
                  // Numbers (integers and decimals)
                  [/\d+\.\d+/, "number"],
                  [/\d+/, "number"],
                  // Strings
                  [/"[^"]*"/, "string"],
                  // Characters
                  [/'.'/, "character"],
                  // Operators
                  [/[+\-*/%<>=!&|~]+/, "operator"],
                  // Function calls
                  [/\b[a-zA-Z_]\w*(?=\()/, "functionIdentifier"],
                  // Identifiers
                  [/\b[a-zA-Z_]\w*\b/, "identifier"],
                  // Brackets and braces
                  [/[\{\}]/, "braces"],
                  [/[\[\]]/, "bracket"],
                  [/[\(\)]/, "parenthesis"],
              ],

              comment: [
              [/[^*]+/, 'comment'],
              [/\*\//, 'comment', '@pop'],
              [/\*/, 'comment'],
              ],
          },
      });

      monaco.languages.setLanguageConfiguration("gal", {
          comments: {
              blockComment: ["/*", "*/"],
              lineComment: "//"          
          },
          autoClosingPairs: [
            { open: '{', close: '}' },
            { open: '[', close: ']' },
            { open: '(', close: ')' },
            { open: '"', close: '"'},
            { open: "'", close: "'"},
            { open: '/*', close: '*/'},
          ],
      });
      
      monaco.editor.defineTheme("galTheme", {
      base: "vs-dark",
      inherit: true,
      rules: [
        { token: "type", foreground: "#89CFF0", fontStyle: "bold"},
        { token: "advancedType", foreground: "#D4A5FF", fontStyle: "bold"},
        { token: "control", foreground: "#FFD36E", fontStyle: "bold"},
        { token: "io", foreground: "#FF8A5B"},
        { token: "boolean", foreground: "#B6FF85"},
        { token: "number", foreground: "#FFE7AF"},
        { token: "string", foreground: "#A6E3A1"},
        { token: "character", foreground: "#A6E3A1"},
        { token: "operator", foreground: "#F2FFEF"},
        { token: "identifier", foreground: "#E0FFD9"},
        { token: "functionIdentifier", foreground: "#FF8A5B", fontStyle: "bold"},
        { token: "braces", foreground: "#7CD26F"},
        { token: "bracket", foreground: "#7CD26F"},
        { token: "parenthesis", foreground: "#F2FFEF"},
        { token: "comment", foreground: "#6D8F74", fontStyle: "italic" },
      ],
        colors: {
          "editor.foreground": "#F2FFEF",
          "editor.background": "#18361D",
          "editorCursor.foreground": "#F2FFEF",
          "editor.lineHighlightBackground": "#204B27",
          "editorLineNumber.foreground": "#A6C3A9",
          "editorindentGuide.background": "#2A5A35",
          "editorindentGuide.activebackground": "#3A7D4A",
          "scrollbarSlider.background": "#0F2014",
          "scrollbarSlider.hoverBackground": "#15301E",
          "scrollbarSlider.activeBackground": "#224B2B"
        }
      });

      window.editor = monaco.editor.create(document.getElementById('editor'), {
        value: `root(){\n\tplant("Hello Garden!");\n\t\n\treclaim;\n}`,
              language: 'gal',
              theme: 'galTheme',
              minimap: { enabled: false },
              overviewRulerLanes: 0,
              automaticLayout: true,
              newLineCharacter: "\n",
              suggest: {
                  filterGraceful: false,
                  showWords: false,
                  enabled: false,
              },
              scrollbar: {
                  vertical: "auto",
                  horizontal: "auto",
                  alwaysConsumeMouseWheel: false,
                  verticalScrollbarSize: 10,
                  horizontalScrollbarSize: 10,
              },
              // Mobile optimizations
              quickSuggestions: false,
              parameterHints: { enabled: false },
              codeLens: false,
              folding: false,
              lineDecorationsWidth: 0,
              lineNumbersMinChars: 3,
              renderLineHighlight: 'line',
              occurrencesHighlight: false,
              selectionHighlight: false,
              renderValidationDecorations: 'on',
          });

          // Add line highlighting on click
          let currentLineDecCollection = editor.createDecorationsCollection([]);
          editor.onDidChangeCursorPosition((e) => {
            const lineNumber = e.position.lineNumber;
            currentLineDecCollection.set([
              {
                range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                options: {
                  isWholeLine: true,
                  className: 'current-line-highlight',
                  glyphMarginClassName: 'current-line-glyph'
                }
              }
            ]);
          });

          // (reverted) no status bar cursor updates

          // ── Bracket mismatch highlighting ──
          let bracketDecCollection = editor.createDecorationsCollection([]);
          const BRACKET_PAIRS = { '(': ')', '[': ']', '{': '}' };
          const CLOSE_TO_OPEN = { ')': '(', ']': '[', '}': '{' };

          function findUnmatchedBrackets(text) {
            const unmatched = [];
            const stack = [];
            let inString = false, inChar = false, inLineComment = false, inBlockComment = false;
            let line = 1, col = 1;
            for (let i = 0; i < text.length; i++) {
              const ch = text[i];
              const next = text[i + 1];
              // Track newlines
              if (ch === '\n') { line++; col = 1; inLineComment = false; continue; }
              // Block comment
              if (inBlockComment) {
                if (ch === '*' && next === '/') { inBlockComment = false; i++; col += 2; }
                else col++;
                continue;
              }
              // Line comment
              if (inLineComment) { col++; continue; }
              // String literal
              if (inString) { if (ch === '"') inString = false; col++; continue; }
              // Char literal
              if (inChar) { if (ch === "'") inChar = false; col++; continue; }
              // Start of comment
              if (ch === '/' && next === '/') { inLineComment = true; col++; continue; }
              if (ch === '/' && next === '*') { inBlockComment = true; i++; col += 2; continue; }
              if (ch === '#') { inLineComment = true; col++; continue; }
              // Start of string/char
              if (ch === '"') { inString = true; col++; continue; }
              if (ch === "'") { inChar = true; col++; continue; }
              // Bracket matching
              if (BRACKET_PAIRS[ch]) {
                stack.push({ ch, line, col });
              } else if (CLOSE_TO_OPEN[ch]) {
                if (stack.length && stack[stack.length - 1].ch === CLOSE_TO_OPEN[ch]) {
                  stack.pop();
                } else {
                  unmatched.push({ line, col });  // unmatched closer
                }
              }
              col++;
            }
            // Remaining in stack = unmatched openers
            stack.forEach(b => unmatched.push({ line: b.line, col: b.col }));
            return unmatched;
          }

          function updateBracketHighlights() {
            const text = editor.getValue();
            const bad = findUnmatchedBrackets(text);
            const decs = bad.map(b => ({
              range: new monaco.Range(b.line, b.col, b.line, b.col + 1),
              options: {
                inlineClassName: 'bracket-mismatch',
                hoverMessage: { value: '**Unmatched bracket**' },
                overviewRuler: { color: '#ff3322', position: monaco.editor.OverviewRulerLane.Center }
              }
            }));
            bracketDecCollection.set(decs);
          }

          // ── Missing semicolon detection ──
          let semicolonDecCollection = editor.createDecorationsCollection([]);

          function findMissingSemicolons(text) {
            const lines = text.split('\n');
            const missing = [];
            let inBlockComment = false;
            for (let i = 0; i < lines.length; i++) {
              const raw = lines[i];
              const trimmed = raw.trim();
              // Track block comments
              if (inBlockComment) {
                if (trimmed.includes('*/')) inBlockComment = false;
                continue;
              }
              if (trimmed.startsWith('/*')) {
                if (!trimmed.includes('*/')) inBlockComment = true;
                continue;
              }
              // Skip empty lines, line comments, and brace-only lines
              if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('#')) continue;
              // Strip inline comments to get actual code
              const codePart = trimmed.replace(/\/\/.*$/, '').trimEnd();
              if (!codePart) continue;
              // Skip lines that end with { or } (block openers/closers)
              if (/[{}]\s*$/.test(codePart)) continue;
              // Skip lines that are only a closing brace or opening brace
              if (/^[{}]+$/.test(codePart)) continue;
              // Skip variety/soil case labels (with or without inline comment)
              if (/^(variety|soil)\b/.test(codePart) && codePart.endsWith(':')) continue;
              // Skip control flow lines ending with ) — they need { not ;
              if (/^(cultivate|grow|tend|spring|bud|pollinate|root)\b.*\)\s*$/.test(codePart)) continue;
              // If line doesn't end with ; it's missing one
              if (!codePart.endsWith(';') && !codePart.endsWith(':') && !codePart.endsWith('{') && !codePart.endsWith('}')) {
                const lineNum = i + 1;
                // Find where code ends (before any inline comment) for ghost placement
                const commentIdx = raw.indexOf('//');
                const codeEnd = commentIdx >= 0 ? raw.substring(0, commentIdx).trimEnd().length : raw.trimEnd().length;
                missing.push({ line: lineNum, col: codeEnd });
              }
            }
            return missing;
          }

          function updateSemicolonWarnings() {
            const model = editor.getModel();
            const text = editor.getValue();
            const bad = findMissingSemicolons(text);
            // Yellow squiggly underlines via model markers
            const markers = bad.map(b => ({
              severity: monaco.MarkerSeverity.Warning,
              startLineNumber: b.line,
              startColumn: Math.max(1, b.col - 1),
              endLineNumber: b.line,
              endColumn: b.col + 1,
              message: 'Missing semicolon ;'
            }));
            monaco.editor.setModelMarkers(model, 'gal-semicolons', markers);
            // Ghost ";" after the last code character (not after comments)
            const decs = bad.map(b => ({
              range: new monaco.Range(b.line, b.col, b.line, b.col + 1),
              options: {
                afterContentClassName: 'semicolon-ghost',
                overviewRuler: { color: '#ff9900', position: monaco.editor.OverviewRulerLane.Center }
              }
            }));
            semicolonDecCollection.set(decs);
          }

          editor.onDidChangeModelContent(() => {
            updateBracketHighlights();
            updateSemicolonWarnings();
            if (window.markDirty) window.markDirty();
          });
          // Initial check
          updateBracketHighlights();
          updateSemicolonWarnings();

          // ── Error line highlighting ──
          let errorDecCollection = editor.createDecorationsCollection([]);

          // Parse error string for line/col: supports "LEXICAL/SYNTAX error line X col Y" and "Ln X Semantic Error"
          function parseErrorLocations(errors) {
            const locs = [];
            const re1 = /(?:LEXICAL|SYNTAX)\s+error\s+line\s+(\d+)\s+col\s+(\d+)/i;
            const re2 = /^Ln\s+(\d+)\s/i;
            (errors || []).forEach(err => {
              const s = String(err);
              let m = re1.exec(s);
              if (m) { locs.push({ line: parseInt(m[1],10), col: parseInt(m[2],10), msg: s }); return; }
              m = re2.exec(s);
              if (m) { locs.push({ line: parseInt(m[1],10), col: 1, msg: s }); }
            });
            return locs;
          }

          window._highlightErrors = function(errors) {
            const locs = parseErrorLocations(errors);
            if (!locs.length) {
              errorDecCollection.set([]);
              monaco.editor.setModelMarkers(window.editor.getModel(), 'gal-errors', []);
              return;
            }
            // Decoration overlays (red tinted line)
            const decorations = locs.map(loc => ({
              range: new monaco.Range(loc.line, 1, loc.line, 1),
              options: {
                isWholeLine: true,
                className: 'error-line-highlight',
                glyphMarginClassName: 'error-line-glyph',
                overviewRuler: { color: '#ff3322', position: monaco.editor.OverviewRulerLane.Full },
                hoverMessage: { value: loc.msg }
              }
            }));
            errorDecCollection.set(decorations);
            // Also set model markers (squiggly red underlines)
            const markers = locs.map(loc => ({
              severity: monaco.MarkerSeverity.Error,
              startLineNumber: loc.line,
              startColumn: loc.col,
              endLineNumber: loc.line,
              endColumn: loc.col + 20,
              message: loc.msg
            }));
            monaco.editor.setModelMarkers(window.editor.getModel(), 'gal-errors', markers);
            // Auto-scroll to first error
            const first = locs[0];
            window.editor.revealLineInCenter(first.line);
            window.editor.setPosition({ lineNumber: first.line, column: first.col });
          };

          window._clearErrorHighlights = function() {
            errorDecCollection.set([]);
            monaco.editor.setModelMarkers(window.editor.getModel(), 'gal-errors', []);
          };
      });
      
  require(['vs/editor/editor.main', 'xterm/xterm', 'xterm-addon-fit'], function (_, Xterm, FitAddon) {

          const term = new Xterm.Terminal({
            cursorBlink: true,
            cursorStyle: 'bar',
            scrollback: 5000,
            rows: 20,
            
            theme: {
              background: '#102417',
              foreground: '#f2ffef',
              cursor: '#f2ffef',
              FontFace: 'monospace',
              fontStyle: 'bold',
            },
          });
          
          fitAddon = new FitAddon.FitAddon();
          term.loadAddon(fitAddon);
      
          term.open(document.getElementById('terminal'));
          window._galTerm = term;  // Expose globally for inline scripts
          window.fitAddon = fitAddon;  // Expose for height resizer
          
          setTimeout(() => term.focus(), 100);
          term.write('Terminal Ready\r\n');

          fitAddon.fit();
        
          window.addEventListener('resize', () => {
            fitAddon.fit();
          });

          // HUD removed: no coins/energy UI

          // Toolbar buttons
          const btnRun = document.getElementById('btn-run');
          const btnLex = document.getElementById('btn-lex');
          // File menu (New/Open/Save/Clear) is handled in index.html inline script

          // Terminal header actions
          let autoScroll = true;
          const autoBtn = document.getElementById('term-autoscroll');
          const copyBtn = document.getElementById('term-copy');
          const clearBtn = document.getElementById('term-clear');
          const toggleMobileLexBtn = document.getElementById('toggle-mobile-lexemes-nav');

          if (autoBtn) {
            autoBtn.setAttribute('aria-pressed', 'true');
            autoBtn.addEventListener('click', () => {
              autoScroll = !autoScroll;
              autoBtn.setAttribute('aria-pressed', String(autoScroll));
            });
          }

          if (copyBtn) {
            copyBtn.addEventListener('click', async () => {
              try {
                const buffer = term.buffer.active;
                let lines = [];
                for (let i = 0; i < buffer.length; i++) {
                  const line = buffer.getLine(i);
                  if (line) lines.push(line.translateToString());
                }
                // Trim trailing empty lines from the buffer
                while (lines.length > 0 && lines[lines.length - 1].trim() === '') {
                  lines.pop();
                }
                await navigator.clipboard.writeText(lines.join('\n') + '\n');
              } catch (e) {
                console.warn('Copy failed:', e);
              }
            });
          }

          if (clearBtn) {
            clearBtn.addEventListener('click', () => term.clear());
          }

          // ── Font size +/- ──
          const FONT_MIN = 8, FONT_MAX = 24;
          let termFontSize = 14;
          const fontDecBtn = document.getElementById('term-font-dec');
          const fontIncBtn = document.getElementById('term-font-inc');
          function updateFontBtnStates() {
            if (fontDecBtn) fontDecBtn.disabled = termFontSize <= FONT_MIN;
            if (fontIncBtn) fontIncBtn.disabled = termFontSize >= FONT_MAX;
          }
          updateFontBtnStates();
          if (fontDecBtn) {
            fontDecBtn.addEventListener('click', () => {
              if (termFontSize <= FONT_MIN) return;
              termFontSize--;
              term.options.fontSize = termFontSize;
              fitAddon.fit();
              updateFontBtnStates();
            });
          }
          if (fontIncBtn) {
            fontIncBtn.addEventListener('click', () => {
              if (termFontSize >= FONT_MAX) return;
              termFontSize++;
              term.options.fontSize = termFontSize;
              fitAddon.fit();
              updateFontBtnStates();
            });
          }

          // Terminal download button removed

          // Mobile lexeme table toggle (navbar button)
          if (toggleMobileLexBtn) {
            const mobileTokensSection = document.querySelector('.mobile-tokens');
            const backdrop = document.getElementById('mobile-tokens-backdrop');
            const toggleIcon = document.getElementById('lexeme-toggle-icon');
            const closeBtn = document.getElementById('mobile-tokens-close');
            
            const closeLexemeTable = () => {
              if (mobileTokensSection) mobileTokensSection.classList.remove('show');
              if (backdrop) backdrop.classList.remove('show');
              if (toggleMobileLexBtn) toggleMobileLexBtn.setAttribute('aria-expanded', 'false');
              if (toggleIcon) toggleIcon.textContent = '▼';
            };
            
            toggleMobileLexBtn.addEventListener('click', () => {
              if (!mobileTokensSection) return;
              
              const isShowing = mobileTokensSection.classList.toggle('show');
              if (backdrop) backdrop.classList.toggle('show', isShowing);
              
              toggleMobileLexBtn.setAttribute('aria-expanded', String(isShowing));
              if (toggleIcon) {
                toggleIcon.textContent = isShowing ? '▲' : '▼';
              }
            });
            
            // Close when clicking close button
            if (closeBtn) {
              closeBtn.addEventListener('click', closeLexemeTable);
            }
            
            // Close when clicking backdrop
            if (backdrop) {
              backdrop.addEventListener('click', closeLexemeTable);
            }
          }

          // Mobile status popup toggle
          (function() {
            const fab = document.getElementById('mobile-status-fab');
            const popup = document.getElementById('mobile-status-popup');
            const backdrop = document.getElementById('mobile-status-backdrop');
            const closeBtn = document.getElementById('mobile-status-close');

            if (!fab || !popup) return;

            const syncChips = () => {
              let hasError = false;
              popup.querySelectorAll('.mobile-status-chip[data-mirror]').forEach(chip => {
                const src = document.getElementById(chip.dataset.mirror);
                if (src) {
                  chip.textContent = src.textContent;
                  chip.className = 'mobile-status-chip';
                  if (src.classList.contains('ok')) chip.classList.add('ok');
                  if (src.classList.contains('err')) { chip.classList.add('err'); hasError = true; }
                }
              });
              // Update FAB indicator color
              const fabIcon = fab.querySelector('.mobile-status-fab-icon');
              if (fabIcon) fabIcon.style.color = hasError ? '#ff8a5b' : '#7cd26f';
            };

            const closePopup = () => {
              popup.classList.remove('show');
              if (backdrop) backdrop.classList.remove('show');
            };

            fab.addEventListener('click', () => {
              syncChips();
              const isShowing = popup.classList.toggle('show');
              if (backdrop) backdrop.classList.toggle('show', isShowing);
            });

            if (closeBtn) closeBtn.addEventListener('click', closePopup);
            if (backdrop) backdrop.addEventListener('click', closePopup);
          })();


  window.runLexer = async function (options = {}) {
      const silent = options.silent === true;
      const sourceCode = editor.getValue();
      console.log("Running lexer with source code:", sourceCode);
    if (!silent) {
      // Separate runs with a blank line
      term.write('\r\n');
    }
          
              try {
          const response = await fetch(`${API_BASE}/api/lex`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ source_code: sourceCode })
                  });
          
                  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
          
                  const data = await response.json();
                  console.log("Lexer response:", data);
          
                  const tokensTableBody = document.getElementById('tokenBody');
                  tokensTableBody.innerHTML = '';
                  const tokensTableBodySide = document.getElementById('tokenBodySide');
                  if (tokensTableBodySide) tokensTableBodySide.innerHTML = '';
                  const tokensTableBodyMobile = document.getElementById('tokenBodyMobile');
                  if (tokensTableBodyMobile) tokensTableBodyMobile.innerHTML = '';

                  // Map backend token types to display names (Token column)
                  const displayType = (tok) => {
                    // For identifiers, show 'id' token type
                    if (tok.type === 'idf' || tok.type === 'id' || tok.type === 'TT_IDENTIFIER') {
                      return 'id';
                    }

                    // For literals, show the token type name
                    if (tok.type === 'intlit' || tok.type === 'TT_INTEGERLIT' || tok.type === 'seedlit') return 'intlit';
                    if (tok.type === 'dbllit' || tok.type === 'TT_DOUBLELIT' || tok.type === 'treelit') return 'dbllit';
                    if (tok.type === 'stringlit' || tok.type === 'strlit' || tok.type === 'strnglit' || tok.type === 'TT_STRINGLIT') return 'stringlit';
                    if (tok.type === 'chrlit' || tok.type === 'TT_CHARLIT' || tok.type === 'leaflit') return 'chrlit';

                    // Special case for branch -> t/f
                    if (tok.type === 'branch') return 't/f';

                    // Boolean literals: sunshine and frost show their keyword as token
                    if (tok.type === 'sunshine') return 'sunshine';
                    if (tok.type === 'frost') return 'frost';
                    
                    // Reserved words are their type directly
                    const kwSet = new Set(['water','plant','seed','leaf','branch','tree','spring','wither','bud','harvest','grow','cultivate','tend','empty','prune','skip','reclaim','root','pollinate','variety','fertile','soil','bundle','vine']);
                    if (kwSet.has(tok.type)) return tok.type;

                    // Show symbols in the Token column as the actual symbol
                    const SYMBOLS = new Set(['+','-','*','/','%','=','==','===','+=','-=','*=','/=','%=','<','>','<=','>=','!=','&&','&','||','|','!','++','--','~','`','(',')','{','}','[',']',',',';',';',':','.']);
                    if (tok && typeof tok.value === 'string' && SYMBOLS.has(tok.value)) return tok.value;
                    if (tok && typeof tok.type === 'string' && SYMBOLS.has(tok.type)) return tok.type;

                    // Fallback for any other token types from old or new lexer
                    if (tok.type && tok.type.startsWith('TT_')) {
                      // If value looks like a symbol, prefer it
                      if (typeof tok.value === 'string' && SYMBOLS.has(tok.value)) return tok.value;
                      return tok.type.substring(3).toLowerCase();
                    }
                    return tok.type || '';
                  };

                  // Determine token classification (Type column)
                  const RESERVED = new Set([
                    'water','plant','seed','leaf','branch','tree','spring','wither','bud','harvest','grow','cultivate','tend','empty','prune','skip','reclaim','root','pollinate','variety','fertile','soil','bundle','vine'
                  ]);
                  const SYMBOLS = new Set(['+','-','*','/','%','=','==','+=','-=','*=','/=','%=','<','>','<=','>=','!=','&&','||','!','++','--','~','`','(',')','{','}','[',']',',',';',';',':','.']);
                  const symbolTypeName = (sym) => {
                    if (sym === '{') return 'R_Curly';
                    if (sym === '}') return 'L_Curly';
                    if (sym === '(') return 'L_Paren';
                    if (sym === ')') return 'R_Paren';
                    if (sym === '[') return 'L_Brkt';
                    if (sym === ']') return 'R_Brkt';
                    if (sym === ',') return 'Comma';
                    if (sym === ';') return 'Semi_c';
                    if (sym === ':') return 'Colon';
                    if (sym === '.') return 'Dot';
                    return '';
                  };
                  const classifyType = (tok) => {
                    const t = tok.type || '';
                    // Keep only these categories in Type column
                    if (RESERVED.has(t)) return 'RW';
                    if (t === 'idf' || t === 'id' || t === 'TT_IDENTIFIER') return 'ID';
                    if (t === 'intlit' || t === 'TT_INTEGERLIT') return 'integer';
                    if (t === 'dbllit' || t === 'TT_DOUBLELIT' || t === 'treelit') return 'double';
                    if (t === 'stringlit' || t === 'strlit' || t === 'strnglit' || t === 'TT_STRINGLIT') return 'string';
                    if (t === 'chrlit' || t === 'TT_CHARLIT') return 'character';
                    // Boolean literals
                    if (t === 'sunshine' || t === 'frost') return 'false';
                    // Operators are labeled 'operator'
                    const OPS = new Set(['+','-','*','/','%','=','==','+=','-=','*=','/=','%=','<','>','<=','>=','!=','&&','||','!','++','--','~','`']);
                    const lex = (tok.value == null ? '' : String(tok.value));
                    if (OPS.has(lex) || OPS.has(t)) return 'operator';
                    // Symbols like braces/parens get specific names
                    if (SYMBOLS.has(lex)) return symbolTypeName(lex);
                    if (SYMBOLS.has(t)) return symbolTypeName(t);
                    // Everything else (operators etc.) blank
                    return '';
                  };
          
                  // Filter out tokens we don't want displayed in the lexeme tables
                  const visibleTokens = (data.tokens || []).filter(t => t && t.type !== 'TT_NL' && t.type !== 'TT_EOF' && t.type !== 'EOF');
                  
                  // Operator tokens should show description in TYPE column
                  const operatorTokens = new Set(['+', '-', '*', '/', '%', '**', '~', '++', '--', 
                    '=', '+=', '-=', '*=', '/=', '%=', '==', '!=', '<', '>', '<=', '>=', 
                    '&&', '||', '!', '`']);
                  
                  visibleTokens.forEach(token => {
                      const vDisp = token.value == null ? '' : String(token.value); // Lexeme column
                      const tDisp = displayType(token); // Token column - use displayType instead of raw type
                      // TYPE column: use description for operators, classifyType for others
                      const cDisp = operatorTokens.has(token.type) ? (token.description || classifyType(token)) : classifyType(token);

                      const row = tokensTableBody.insertRow();
                      row.insertCell(0).textContent = vDisp;
                      row.insertCell(1).textContent = tDisp;
                      row.insertCell(2).textContent = cDisp;

                      if (tokensTableBodySide){
                        const r = tokensTableBodySide.insertRow();
                        r.insertCell(0).textContent = vDisp;
                        r.insertCell(1).textContent = tDisp;
                        r.insertCell(2).textContent = cDisp;
                      }

                      if (tokensTableBodyMobile){
                        const m = tokensTableBodyMobile.insertRow();
                        m.insertCell(0).textContent = vDisp;
                        m.insertCell(1).textContent = tDisp;
                        m.insertCell(2).textContent = cDisp;
                      }
                  });

                  // No table content mirrored to terminal output
          
  if (data.errors.length > 0) {
            if (!silent) {
            data.errors.forEach(err => {
              term.write(`\x1b[1;31m${err}\x1b[0m\r\n`);
            });
            }
            if (!silent && window._highlightErrors) window._highlightErrors(data.errors);
            const sl = document.getElementById('status-lex');
            if (sl){ sl.classList.remove('ok'); sl.classList.add('err'); sl.textContent = 'Lexical: Error'; }
      } else {
            if (!silent && window._clearErrorHighlights) window._clearErrorHighlights();
            if (!silent) term.write('Lexical analysis successful!\r\n');
            const sl = document.getElementById('status-lex');
            if (sl){ sl.classList.remove('err'); sl.classList.add('ok'); sl.textContent = 'Lexical: OK'; }
    return true;
                  }
          
              } catch (error) {
          console.error("Error running lexical analysis:", error);
          if (!silent) term.write('Error running lexical analysis.\r\n');
                  return false;
              }
          };

          window.runSyntax = async function (options = {}) {
            const silent = options.silent === true;
            const sourceCode = editor.getValue();
            console.log("Running syntax analysis with source code:", sourceCode);
            if (!silent) {
              term.write('\r\n');
            }
            
            // Run lexer first to populate the token table
            await runLexer({ silent: true });
            
            try {
              const response = await fetch(`${API_BASE}/api/parse`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source_code: sourceCode })
              });
              
              if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
              
              const data = await response.json();
              console.log("Parser response:", data);

              // Update status chips
              const sl = document.getElementById('status-lex');
              const ss = document.getElementById('status-syn');
              
              // Check if stage is an array or string
              const stages = Array.isArray(data.stage) ? data.stage : [data.stage];
              const hasLexicalErrors = stages.includes('lexical') || data.lexical_errors;
              const hasSyntaxErrors = stages.includes('syntax') || data.syntax_errors;
              
              if (data.errors && data.errors.length > 0) {
                if (!silent) {
                  data.errors.forEach(err => term.write(`\x1b[1;31m${err}\x1b[0m\r\n`));
                }
                if (window._highlightErrors) window._highlightErrors(data.errors);
              } else {
                if (window._clearErrorHighlights) window._clearErrorHighlights();
              }
              
              if (hasLexicalErrors) {
                if (sl) { sl.classList.remove('ok'); sl.classList.add('err'); sl.textContent = 'Lexical: Error'; }
              } else {
                if (sl) { sl.classList.remove('err'); sl.classList.add('ok'); sl.textContent = 'Lexical: OK'; }
              }
              
              if (hasSyntaxErrors) {
                if (ss) { ss.classList.remove('ok'); ss.classList.add('err'); ss.textContent = 'Syntax: Error'; }
              } else {
                if (ss) { ss.classList.remove('err'); ss.classList.add('ok'); ss.textContent = 'Syntax: OK'; }
              }
              
              if (data.success && !hasLexicalErrors && !hasSyntaxErrors) {
                if (!silent) term.write('Syntax analysis successful!\r\n');
                return true;
              }
              
            } catch (error) {
              console.error("Error running syntax analysis:", error);
              if (!silent) term.write('Error running syntax analysis.\r\n');
              return false;
            }
          };

          // Semantic Analysis Function
          window.runSemantic = async function (options = {}) {
            const silent = options.silent || false;
            const sourceCode = editor.getValue();
            console.log("Running semantic analysis with source code:", sourceCode);
            
            // Run lexer first to populate the token table
            await runLexer({ silent: true });
            
            try {
              const response = await fetch(`${API_BASE}/api/semantic`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source_code: sourceCode })
              });
              
              const data = await response.json();
              console.log("Semantic response:", data);
              
              // Clear terminal and display analysis results
              term.clear();
              const sl = document.getElementById('status-lex');
              const ss = document.getElementById('status-syn');
              const ssem = document.getElementById('status-sem');
              
              if (data.stage === 'lexical' && data.errors.length > 0) {
                // Lexical errors
                if (!silent) {
                  term.write('Lexical Errors:\r\n');
                  data.errors.forEach(err => term.write(`  ${err}\r\n`));
                }
                if (sl) { sl.classList.remove('ok'); sl.classList.add('err'); sl.textContent = 'Lexical: Error'; }
                if (ss) { ss.classList.remove('ok', 'err'); ss.textContent = 'Syntax: —'; }
                if (ssem) { ssem.classList.remove('ok', 'err'); ssem.textContent = 'Semantic: —'; }
                if (window._highlightErrors) window._highlightErrors(data.errors);
              } else if (data.stage === 'syntax' && data.errors.length > 0) {
                // Syntax errors
                if (!silent) {
                  term.write('Syntax Errors:\r\n');
                  data.errors.forEach(err => term.write(`  ${err}\r\n`));
                }
                if (sl) { sl.classList.remove('err'); sl.classList.add('ok'); sl.textContent = 'Lexical: OK'; }
                if (ss) { ss.classList.remove('ok'); ss.classList.add('err'); ss.textContent = 'Syntax: Error'; }
                if (ssem) { ssem.classList.remove('ok', 'err'); ssem.textContent = 'Semantic: —'; }
                if (window._highlightErrors) window._highlightErrors(data.errors);
              } else if (data.stage === 'semantic') {
                // Semantic analysis results
                if (!silent) {
                  if (data.errors.length > 0) {
                    term.write('Semantic analysis error!\r\n');
                    data.errors.forEach(err => term.write(`  ${err}\r\n`));
                  } else {
                    term.write('Semantic analysis passed!\r\n');
                  }
                }
                
                if (sl) { sl.classList.remove('err'); sl.classList.add('ok'); sl.textContent = 'Lexical: OK'; }
                if (ss) { ss.classList.remove('err'); ss.classList.add('ok'); ss.textContent = 'Syntax: OK'; }
                if (ssem) {
                  if (data.errors.length > 0) {
                    ssem.classList.remove('ok'); ssem.classList.add('err'); ssem.textContent = 'Semantic: Error';
                    if (window._highlightErrors) window._highlightErrors(data.errors);
                  } else {
                    ssem.classList.remove('err'); ssem.classList.add('ok'); ssem.textContent = 'Semantic: OK';
                    if (window._clearErrorHighlights) window._clearErrorHighlights();
                  }
                }
              }
            } catch (error) {
              console.error("Error running semantic analysis:", error);
              if (!silent) term.write('Error running semantic analysis.\\r\\n');
            }
          };

          // Syntax analysis removed; only lexical phase retained.
          
          // ─── Run / Execute Program ─────────────────────────────

          // Helper: update status chips from a stage/success result
          function updateStatusChips(stage, success) {
            const sl  = document.getElementById('status-lex');
            const ss  = document.getElementById('status-syn');
            const ssem = document.getElementById('status-sem');
            const sexe = document.getElementById('status-exe');

            if (stage === 'lexical') {
              if (sl) { sl.classList.add('err'); sl.textContent = 'Lexical: Error'; }
            } else if (stage === 'syntax') {
              if (sl) { sl.classList.add('ok'); sl.textContent = 'Lexical: OK'; }
              if (ss) { ss.classList.add('err'); ss.textContent = 'Syntax: Error'; }
            } else if (stage === 'semantic') {
              if (sl) { sl.classList.add('ok'); sl.textContent = 'Lexical: OK'; }
              if (ss) { ss.classList.add('ok'); ss.textContent = 'Syntax: OK'; }
              if (ssem) { ssem.classList.add('err'); ssem.textContent = 'Semantic: Error'; }
            } else if (stage === 'execution') {
              if (sl) { sl.classList.add('ok'); sl.textContent = 'Lexical: OK'; }
              if (ss) { ss.classList.add('ok'); ss.textContent = 'Syntax: OK'; }
              if (ssem) { ssem.classList.add('ok'); ssem.textContent = 'Semantic: OK'; }
              if (success) {
                if (sexe) { sexe.classList.add('ok'); sexe.textContent = 'Execution: OK'; }
              } else {
                if (sexe) { sexe.classList.add('err'); sexe.textContent = 'Execution: Error'; }
              }
            }
          }

          // Run via REST (non-interactive programs)
          async function runViaREST(sourceCode, silent) {
            try {
              const resp = await fetch(`${API_BASE}/api/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source_code: sourceCode })
              });
              const result = await resp.json();

              if (result.output && result.output.length > 0) {
                result.output.forEach(line => {
                  const isError = /error|Error/.test(line);
                  if (isError) {
                    term.write(`\x1b[1;31m${line}\x1b[0m\r\n`);
                  } else {
                    term.write(line + '\r\n');
                  }
                });
              }

              updateStatusChips(result.stage, result.success);

              if (result.stage === 'execution') {
                if (result.success) {
                  if (!silent) term.write('Code execution successful.\r\n');
                } else {
                  if (!silent) term.write('Code execution failed.\r\n');
                }
              }
            } catch (err) {
              if (!silent) term.write('Error: Could not connect to server.\r\n');
              console.error('Run error:', err);
            }
          }

          // Run via Socket.IO (interactive programs with water())
          function runViaSocket(sourceCode, silent) {
            // Reset input state from any previous run
            waitingForInput = false;
            userInput = '';
            // Bump generation and clear collected output
            window._runGeneration = (window._runGeneration || 0) + 1;
            window._socketOutputLog = [];
            // Remove any lingering execution_complete listeners
            socket.removeAllListeners('execution_complete');
            // Ensure socket is connected
            if (!socket.connected) {
              socket.connect();
            }

            // Wait until connected, then emit
            function doEmit() {
              const myGen = window._runGeneration;
              // Remove any stale completion listeners before adding a fresh one
              socket.removeAllListeners('execution_complete');
              // One-time listener for execution_complete
              socket.once('execution_complete', function onComplete(data) {
                if (myGen !== window._runGeneration) return; // stale
                updateStatusChips(data.stage, data.success);
                if (data.stage === 'execution') {
                  if (data.success) {
                    if (!silent) {
                      term.write('\r\n\x1b[1;32mCode execution successful.\x1b[0m\r\n');
                    }
                  } else {
                    if (!silent) {
                      term.write('\r\n\x1b[1;31mCode execution failed.\x1b[0m\r\n');
                    }
                  }
                }
                // Highlight errors from collected socket output
                if (!data.success && window._socketOutputLog && window._socketOutputLog.length > 0) {
                  if (window._highlightErrors) window._highlightErrors(window._socketOutputLog);
                } else {
                  if (window._clearErrorHighlights) window._clearErrorHighlights();
                }
              });
              socket.emit('run_code', { source_code: sourceCode });
            }

            if (socket.connected) {
              doEmit();
            } else {
              socket.once('connect', () => {
                doEmit();
              });
              // Timeout fallback
              setTimeout(() => {
                if (!socket.connected) {
                  if (!silent) term.write('Error: Could not connect to server for interactive mode.\r\n');
                }
              }, 5000);
            }
          }

          window.runProgram = async function (options = {}) {
            const silent = options.silent || false;
            const sourceCode = editor.getValue();

            // Clear previous error highlights
            if (window._clearErrorHighlights) window._clearErrorHighlights();
            // Remove stale socket listeners
            socket.removeAllListeners('execution_complete');

            // Populate the token table in the background (silent — no terminal writes)
            await runLexer({ silent: true });

            // Reset status chips
            const sl  = document.getElementById('status-lex');
            const ss  = document.getElementById('status-syn');
            const ssem = document.getElementById('status-sem');
            const sexe = document.getElementById('status-exe');
            if (sl)   { sl.classList.remove('ok','err');  sl.textContent = 'Lexical: —'; }
            if (ss)   { ss.classList.remove('ok','err');  ss.textContent = 'Syntax: —'; }
            if (ssem) { ssem.classList.remove('ok','err'); ssem.textContent = 'Semantic: —'; }
            if (sexe) { sexe.classList.remove('ok','err'); sexe.textContent = 'Execution: —'; }

            // Check if program uses water() (needs interactive input via Socket.IO)
            const needsInput = /\bwater\s*\(/.test(sourceCode);

            if (needsInput) {
              runViaSocket(sourceCode, silent);
            } else {
              await runViaREST(sourceCode, silent);
            }
          };

          
        // Run generation counter — ignore output from stale/previous runs
        window._runGeneration = 0;
        window._socketOutputLog = [];
        socket.on('output', function (data) {
            // Ignore output from a previous run
            if (data._gen !== undefined && data._gen !== window._runGeneration) return;
            const text = data.output;
            window._socketOutputLog.push(text);
            const isError = /error|Error/.test(text);
            const lines = text.split('\n');
            lines.forEach((line, index) => {
              if (isError) {
                term.write(`\x1b[1;31m${line}\x1b[0m`);
              } else {
                term.write(line);
              }
              if (index < lines.length - 1) {
                term.write('\r\n');
              }
            });
            if (autoScroll) term.scrollToBottom();
            term.focus();
        });

        // Update status chips as each compiler stage completes
        socket.on('stage_complete', function (data) {
            const sl  = document.getElementById('status-lex');
            const ss  = document.getElementById('status-syn');
            const ssem = document.getElementById('status-sem');
            if (data.stage === 'lexical' && data.success) {
              if (sl) { sl.classList.remove('err'); sl.classList.add('ok'); sl.textContent = 'Lexical: OK'; }
            }
            if (data.stage === 'syntax' && data.success) {
              if (ss) { ss.classList.remove('err'); ss.classList.add('ok'); ss.textContent = 'Syntax: OK'; }
            }
            if (data.stage === 'semantic' && data.success) {
              if (ssem) { ssem.classList.remove('err'); ssem.classList.add('ok'); ssem.textContent = 'Semantic: OK'; }
            }
        });
          
        // Register ONE persistent onData listener (only once)
        if (!termInputRegistered) {
          termInputRegistered = true;
          term.onData(function (e) {
            if (!waitingForInput) return;

            if (e === '\x1b[A' || e === '\x1b[B' || e === '\x1b[C' || e === '\x1b[D') {
              return;
            }

            if (e === '\r') {
              term.write('\r\n');
              waitingForInput = false;
              socket.emit('capture_input', { var_name: variable, input: userInput });
              userInput = '';
            } else if (e === '\u007f') {
              if (userInput.length > 0) {
                  userInput = userInput.slice(0, -1); 
                  term.write('\b \b');
              }
            } else {
              userInput += e;
              term.write(e);
            }
          });
        }

        socket.on('input_required', function (data) {
            const prompt = data.prompt;
            variable = data.variable;

            waitingForInput = true;
            userInput = '';  
        });

          // Global variable to track selected run mode
          let currentRunMode = 'run';
          
      window.runCode = async function () {
        // Clear terminal and error highlights at the start of each run
        term.write('\x1b[2J\x1b[3J\x1b[H');
        if (window._clearErrorHighlights) window._clearErrorHighlights();
        // Remove any stale socket listeners from previous runs
        socket.removeAllListeners('execution_complete');
        
        // Use the current run mode
        if (currentRunMode === 'run') {
          await runProgram({ silent: false });
        } else if (currentRunMode === 'syntax') {
          await runSyntax({ silent: false });
        } else if (currentRunMode === 'semantic') {
          await runSemantic({ silent: false });
        } else {
          await runLexer({ silent: false });
        }
      };
      
      window.selectRunMode = function(mode) {
        currentRunMode = mode;
        const modeText = mode.charAt(0).toUpperCase() + mode.slice(1);
        document.getElementById('run-mode-text').textContent = modeText;
        document.getElementById('run-dropdown-menu').classList.add('hidden');
      };
      
      window.toggleRunDropdown = function(event) {
        if (event) {
          event.preventDefault();
          event.stopPropagation();
        }
        const menu = document.getElementById('run-dropdown-menu');
        if (menu) {
          menu.classList.toggle('hidden');
          
          // Position dropdown correctly on mobile
          if (!menu.classList.contains('hidden') && window.innerWidth <= 768) {
            const btn = document.querySelector('.btn-dropdown-toggle');
            if (btn) {
              const rect = btn.getBoundingClientRect();
              menu.style.position = 'fixed';
              menu.style.top = (rect.bottom + 4) + 'px';
              menu.style.right = (window.innerWidth - rect.right) + 'px';
              menu.style.left = 'auto';
            }
          }
        }
      };
      
      // Add touch support for dropdown toggle
      const dropdownToggleBtn = document.querySelector('.btn-dropdown-toggle');
      if (dropdownToggleBtn) {
        dropdownToggleBtn.addEventListener('touchend', function(e) {
          e.preventDefault();
          window.toggleRunDropdown(e);
        }, { passive: false });
      }
      
      // Add touch support for dropdown items
      document.querySelectorAll('.run-dropdown-item').forEach(function(item) {
        item.addEventListener('touchend', function(e) {
          e.preventDefault();
          const mode = this.getAttribute('data-mode');
          if (mode) {
            window.selectRunMode(mode);
          }
        }, { passive: false });
      });
        });

  });
  
  
  document.querySelector(".widthResizer").addEventListener("mousedown", (e) => {
      e.preventDefault();
      document.addEventListener("mousemove", widthResize);
      document.addEventListener("mouseup", () => {
          document.removeEventListener("mousemove", widthResize);
      }, { once: true });
  });

  function widthResize(e) {
      let newWidth = e.clientX - document.querySelector(".textFieldCont").getBoundingClientRect().left;
      document.querySelector(".textFieldCont").style.width = `${newWidth}px`;
  }

  /* ── Height resizer for terminal ── */
  const heightResizer = document.querySelector('.heightResizer');
  if (heightResizer) {
    const workspaceMain = document.querySelector('.workspace-main');
    const mainCont = document.querySelector('.mainCont');
    const termCont = document.querySelector('.terminalCont');

    heightResizer.addEventListener('mousedown', (e) => {
      e.preventDefault();
      heightResizer.classList.add('active');
      document.body.style.cursor = 'ns-resize';
      document.body.style.userSelect = 'none';

      function onMouseMove(ev) {
        const parentRect = workspaceMain.getBoundingClientRect();
        const resizerH = heightResizer.offsetHeight;
        // y position relative to workspace-main
        const y = ev.clientY - parentRect.top;
        const minEditor = 100;
        const minTerminal = 100;
        const available = parentRect.height - resizerH;
        let editorH = Math.max(minEditor, Math.min(y, available - minTerminal));
        let termH = available - editorH;

        mainCont.style.height = editorH + 'px';
        termCont.style.height = termH + 'px';

        // Re-fit xterm
        if (window.fitAddon) window.fitAddon.fit();
      }

      function onMouseUp() {
        heightResizer.classList.remove('active');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
        if (window.fitAddon) window.fitAddon.fit();
      }

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    });

    // Touch support for mobile
    heightResizer.addEventListener('touchstart', (e) => {
      e.preventDefault();
      heightResizer.classList.add('active');

      function onTouchMove(ev) {
        const touch = ev.touches[0];
        const parentRect = workspaceMain.getBoundingClientRect();
        const resizerH = heightResizer.offsetHeight;
        const y = touch.clientY - parentRect.top;
        const minEditor = 100;
        const minTerminal = 100;
        const available = parentRect.height - resizerH;
        let editorH = Math.max(minEditor, Math.min(y, available - minTerminal));
        let termH = available - editorH;

        mainCont.style.height = editorH + 'px';
        termCont.style.height = termH + 'px';
        if (window.fitAddon) window.fitAddon.fit();
      }

      function onTouchEnd() {
        heightResizer.classList.remove('active');
        document.removeEventListener('touchmove', onTouchMove);
        document.removeEventListener('touchend', onTouchEnd);
        if (window.fitAddon) window.fitAddon.fit();
      }

      document.addEventListener('touchmove', onTouchMove);
      document.addEventListener('touchend', onTouchEnd);
    }, { passive: false });
  }

  /* ── Sidebar resizer (drag to resize lexeme panel) ── */
  const sidebarResizer = document.querySelector('.sidebarResizer');
  if (sidebarResizer) {
    const sidebar = document.querySelector('.sidebar');

    sidebarResizer.addEventListener('mousedown', (e) => {
      e.preventDefault();
      sidebarResizer.classList.add('active');
      document.body.style.cursor = 'ew-resize';
      document.body.style.userSelect = 'none';

      function onMouseMove(ev) {
        const workspaceRect = document.querySelector('.workspace').getBoundingClientRect();
        const newWidth = ev.clientX - workspaceRect.left - 12; // 12 = workspace padding
        const clamped = Math.max(200, Math.min(newWidth, workspaceRect.width * 0.7));
        sidebar.style.width = clamped + 'px';
        // Trigger Monaco editor relayout
        if (window.editor && window.editor.layout) window.editor.layout();
      }

      function onMouseUp() {
        sidebarResizer.classList.remove('active');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
        if (window.editor && window.editor.layout) window.editor.layout();
      }

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    });

    // Touch support
    sidebarResizer.addEventListener('touchstart', (e) => {
      e.preventDefault();
      sidebarResizer.classList.add('active');

      function onTouchMove(ev) {
        const touch = ev.touches[0];
        const workspaceRect = document.querySelector('.workspace').getBoundingClientRect();
        const newWidth = touch.clientX - workspaceRect.left - 12;
        const clamped = Math.max(200, Math.min(newWidth, workspaceRect.width * 0.7));
        sidebar.style.width = clamped + 'px';
        if (window.editor && window.editor.layout) window.editor.layout();
      }

      function onTouchEnd() {
        sidebarResizer.classList.remove('active');
        document.removeEventListener('touchmove', onTouchMove);
        document.removeEventListener('touchend', onTouchEnd);
        if (window.editor && window.editor.layout) window.editor.layout();
      }

      document.addEventListener('touchmove', onTouchMove);
      document.addEventListener('touchend', onTouchEnd);
    }, { passive: false });
  }

  function toggleDropdown() {
      const menu = document.getElementById("dropdown-menu");
      menu.classList.toggle("hidden");
    }
    

    
    // Hide dropdown if clicked outside (handles both click and touch)
    function hideDropdownsOnOutsideClick(e) {
      const dropdown = document.querySelector(".dropdown");
      const menu = document.getElementById("dropdown-menu");
    
      if (dropdown && menu && !dropdown.contains(e.target)) {
        menu.classList.add("hidden");
      }
      
      // Hide run dropdown if clicked outside
      const runDropdown = document.querySelector(".run-dropdown");
      const runMenu = document.getElementById("run-dropdown-menu");
      
      if (runDropdown && runMenu && !runDropdown.contains(e.target)) {
        runMenu.classList.add("hidden");
      }
    }
    
    document.addEventListener("click", hideDropdownsOnOutsideClick);
    document.addEventListener("touchstart", hideDropdownsOnOutsideClick, { passive: true });

    // Auto-lex on typing (debounced) to keep sidebar tokens in sync with GALalexer rules
    function debounce(fn, wait){
      let t; return function(...args){ clearTimeout(t); t = setTimeout(() => fn.apply(this, args), wait); };
    }
    const debouncedLex = debounce(() => window.runLexer({ silent: true }), 400);
    if (window.editor && editor.onDidChangeModelContent){
      editor.onDidChangeModelContent(() => {
        debouncedLex();
      });
    }

