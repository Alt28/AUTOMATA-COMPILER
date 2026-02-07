  
  let fitAddon;
  document.addEventListener('DOMContentLoaded', async () => {

  // Auto-target Flask backend when running from a different origin (e.g., VS Code Live Server on 5500)
  const API_BASE = (location.port && location.port !== '5000') ? 'http://localhost:5000' : '';

  // Use same-origin Socket.IO connection for portability (works in Docker and cloud)
  const socketBase = (location.port && location.port !== '5000') ? 'http://localhost:5000' : undefined;
  const socket = socketBase ? io(socketBase) : io();
    let waitingForInput = false;
    let userInput = '';
    let inputCallback = null;
    let variable = '';  // Store the variable name for which we need input
    let termDataListener = null;

    socket.on('connect', () => {
        console.log('Socket.IO connected');
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
                  [/\b(tree|seed|leaf|branch|string)\b/, "type"],
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
        value: `root(){\n\t// your code here\n\t\n}`,
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
              renderValidationDecorations: 'off',
          });

          // Add line highlighting on click
          let currentLineDecorations = [];
          editor.onDidChangeCursorPosition((e) => {
            const lineNumber = e.position.lineNumber;
            // Highlight the current line
            currentLineDecorations = editor.deltaDecorations(currentLineDecorations, [
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
          const btnClear = document.getElementById('btn-clear');
          // Removed Run/Lexical toolbar bindings per UI update
          btnClear && btnClear.addEventListener('click', () => {
            term.clear();
            const tbody = document.getElementById('tokenBody');
            if (tbody) tbody.innerHTML = '';
            const tbodySide = document.getElementById('tokenBodySide');
            if (tbodySide) tbodySide.innerHTML = '';
            ['status-lex','status-syn','status-sem','status-exe'].forEach(id => {
              const el = document.getElementById(id);
              if (el){ el.classList.remove('ok','err'); el.textContent = el.textContent.replace(/:.*/, ': —'); }
            });
          });

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
                let text = '';
                for (let i = 0; i < buffer.length; i++) {
                  const line = buffer.getLine(i);
                  if (line) text += line.translateToString() + '\n';
                }
                await navigator.clipboard.writeText(text);
              } catch (e) {
                console.warn('Copy failed:', e);
              }
            });
          }

          if (clearBtn) {
            clearBtn.addEventListener('click', () => term.clear());
          }

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
                    // For identifiers, show the actual identifier name
                    if (tok.type === 'idf' || tok.type === 'id' || tok.type === 'TT_IDENTIFIER') {
                      return tok.value || 'id';
                    }

                    // For literals, show the actual literal value
                    const literalTypes = new Set(['intlit','dbllit','strnglit','chrlit','TT_INTEGERLIT','TT_DOUBLELIT','TT_STRINGLIT','TT_CHARLIT','seedlit','treelit','leaflit']);
                    if (literalTypes.has(tok.type)) return tok.value != null ? String(tok.value) : '';

                    // Reserved words are their type directly
                    const kwSet = new Set(['water','plant','seed','leaf','branch','tree','spring','wither','bud','harvest','grow','cultivate','tend','empty','prune','skip','reclaim','root','pollinate','variety','fertile','soil','bundle','string']);
                    if (kwSet.has(tok.type)) return tok.type;

                    // Show symbols in the Token column as the actual symbol
                    const SYMBOLS = new Set(['+','-','*','/','%','=','==','+=','-=','*=','/=','%=','<','>','<=','>=','!=','&&','||','!','++','--','~','`','(',')','{','}','[',']',',',';',';',':','.']);
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
                    'water','plant','seed','leaf','branch','tree','spring','wither','bud','harvest','grow','cultivate','tend','empty','prune','skip','reclaim','root','pollinate','variety','fertile','soil','bundle','string'
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
                    if (t === 'strnglit' || t === 'TT_STRINGLIT') return 'string';
                    if (t === 'chrlit' || t === 'TT_CHARLIT') return 'character';
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
                  visibleTokens.forEach(token => {
                      const tDisp = displayType(token);   // Token column
                      const vDisp = token.value == null ? '' : String(token.value); // Lexeme column
                      const cDisp = classifyType(token);  // Token Type column

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
              term.write(`${err}\r\n`);
            });
            }
            const sl = document.getElementById('status-lex');
            if (sl){ sl.classList.remove('ok'); sl.classList.add('err'); sl.textContent = 'Lexical: Error'; }
      } else {
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

          // Syntax analysis removed; only lexical phase retained.
          
          
        socket.on('output', function (data) {
            const lines = data.output.split('\n');
            lines.forEach((line, index) => {
              term.write(line);
              // Only add newline if not the last line or if the original ended with newline
              if (index < lines.length - 1 || data.output.endsWith('\n')) {
                term.write('\r\n');
              }
            });
      if (autoScroll) term.scrollToBottom();
            term.focus(); 
        });
          
        socket.on('input_required', function (data) {
            const prompt = data.prompt;
            variable = data.variable;
    

            waitingForInput = true;
            userInput = '';  

            if (termDataListener) {
              term.offData(termDataListener);
            }
            
            const inputStartPosition = term.cols;

            termDataListener = function (e) {
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

              
          };
  
          term.onData(termDataListener);
        });

          
      window.runCode = async function () {
        // Run lexical analysis (same as Lexical button)
        await runLexer({ silent: false });
      };
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

  function toggleDropdown() {
      const menu = document.getElementById("dropdown-menu");
      menu.classList.toggle("hidden");
    }
    

    
    // Hide dropdown if clicked outside
    document.addEventListener("click", function (e) {
      const dropdown = document.querySelector(".dropdown");
      const menu = document.getElementById("dropdown-menu");
    
      if (!dropdown.contains(e.target)) {
        menu.classList.add("hidden");
      }
    });

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


