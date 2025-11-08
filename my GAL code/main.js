  
  let fitAddon;
  let coins = 0;
  let energy = 100;
  document.addEventListener('DOMContentLoaded', async () => {

    const socket = io.connect('http://localhost:5000');
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

          monaco.languages.register({ id: "cgma" });

          monaco.languages.setMonarchTokensProvider("cgma", {
          tokenizer: {
              
              root: [
                  [/\b(chungus|chudeluxe|forsen|forsencd|lwk|nocap|aura|sturdy)\b/, "type"],
                  [/\b(hawk|tuah|lethimcook|jit|lil|plug)\b/, "control"],
                  [/\b(yap|chat)\b/, "io"],
                  [/\b(append|insert|remove|ts|taper)\b/, "function"],
                  [/\b(continue|getout|back)\b/, "control1"],
                  [/\b(npc|caseoh|fein)\b/, "keyword"],
                  [/\b(true|false)\b/, "boolean"],
                  // Line comments: // ... and # ...
                  [/\/\/.*/, "comment"],
                  [/#.*/, "comment"],
                  [/\/\*/, 'comment', '@comment'],
                  [/\d+/, "number"],
                  [/"[^"]*"/, "string"],
                  [/'[^']*'/, "string"],
                  [/[+\-*/<>!,&|]+/, "operator"],
                  [/\b[a-zA-Z_]\w*(?=\()/, "functionIdentifier"],
                  [/\b[a-zA-Z_]\w*\b/, "identifier"], // Identifiers
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

      monaco.languages.setLanguageConfiguration("cgma", {
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
      
      monaco.editor.defineTheme("myCustomTheme", {
      base: "vs-dark",
      inherit: true,
      rules: [
        { token: "keyword", foreground: "#A6E3A1"},
        { token: "type", foreground: "#7CD26F"},
        { token: "control", foreground: "#A6E3A1"},
        { token: "control1", foreground: "#FFD36E"},
        { token: "function", foreground: "#FF8A5B"},
        { token: "io", foreground: "#B6FF85"},
        { token: "boolean", foreground: "#FFE7AF"},
        { token: "number", foreground: "#FFE7AF"},
        { token: "string", foreground: "#FFE7AF"},
        { token: "operator", foreground: "#F2FFEF"},
        { token: "identifier", foreground: "#E0FFD9", fontStyle: "bold"},
        { token: "functionIdentifier", foreground: "#FFD36E", fontStyle: "bold"},
        { token: "braces", foreground: "#7CD26F", fontStyle: "bold"},
        { token: "bracket", foreground: "#7CD26F"},
        { token: "parenthesis", foreground: "#7CD26F"},
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
              language: 'Grow A Language',
              theme: 'myCustomTheme',
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

          // HUD helpers
          function setCoins(val){ coins = Math.max(0, val); document.getElementById('coinCounter').textContent = coins; }
          function setEnergy(val){
            energy = Math.max(0, Math.min(100, val));
            const fill = document.getElementById('energyFill');
            const label = document.getElementById('energyLabel');
            if (fill) fill.style.width = energy + '%';
            if (label) label.textContent = energy;
          }
          setCoins(0); setEnergy(100);

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


  window.runLexer = async function (options = {}) {
      const silent = options.silent === true;
      const sourceCode = editor.getValue();
      console.log("Running lexer with source code:", sourceCode);
    if (!silent) {
      // Separate runs with a blank line
      term.write('\r\n');
      term.write('Running lexical analysis...\r\n');
      // playful energy/coins feedback
      setEnergy(energy - 2);
    }
          
              try {
                  const response = await fetch('/api/lex', {
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

                  // Map backend token types to display names
                  const displayType = (tok) => {
                    // 1) Keywords: show the lexeme itself (e.g., 'seed')
                    if (tok.type && tok.type.startsWith('TT_RW_')){
                      return tok.value || tok.type.replace('TT_RW_', '').toLowerCase();
                    }
                    // 2) Identifiers: standardized label
                    if (tok.type === 'TT_IDENTIFIER') return 'IDF';
                    // 3) Symbols/operators: show the literal symbol(s) as the type (e.g., ')', '==', '{', ';')
                    if (typeof tok.value === 'string' && /^[^A-Za-z0-9_]+$/.test(tok.value)){
                      return tok.value;
                    }
                    // 4) Everything else: trim the TT_ prefix for readability
                    if (tok.type && tok.type.startsWith('TT_')) return tok.type.substring(3);
                    return tok.type || '';
                  };
          
                  data.tokens.forEach(token => {
                      const tDisp = displayType(token);
                      const vDisp = token.value == null ? '' : String(token.value);

                      const row = tokensTableBody.insertRow();
                      row.insertCell(0).textContent = vDisp;
                      row.insertCell(1).textContent = tDisp;

                      if (tokensTableBodySide){
                        const r = tokensTableBodySide.insertRow();
                        r.insertCell(0).textContent = vDisp;
                        r.insertCell(1).textContent = tDisp;
                      }
                  });
          
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

          // Syntax and Semantic analysis functions removed per request
          
          
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
        // Separate runs with a blank line
        term.write('\r\n');
        term.write('Running program...\r\n');

              // Only require lexical analysis before running code
              const lexerSuccess = await runLexer();
              if (!lexerSuccess) {
                  return;
              }

              await new Promise(resolve => setTimeout(resolve, 10));

              const sourceCode = editor.getValue();

              try {
                const response = await fetch('/api/output', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ source_code: sourceCode })
                });

                const data = await response.json();

                if (!data.success) {
                  if (data.errors) {
                    data.errors.forEach(err => {
                      term.write(`${err}\r\n`);
                    });
                  }
                  return;
                }
                setCoins(coins + 10);
                setEnergy(Math.min(100, energy + 5));

              } catch (error) {
                console.error("Error running source code:", error);
                term.write('Error running source code.\r\n');
              }
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
    
    // (reverted) no activity bar toggles
    
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


