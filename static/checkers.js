document.addEventListener('DOMContentLoaded', function() {
    // Screen elements
    const homeScreen = document.getElementById('home-screen');
    const settingsScreen = document.getElementById('settings-screen');
    const gameScreen = document.getElementById('game-screen');

    // Buttons
    const playButton = document.getElementById('play-button');
    const settingsButton = document.getElementById('settings-button');
    const backFromSettingsButton = document.getElementById('back-from-settings');
    const backToHomeButton = document.getElementById('back-to-home');
    const saveSettingsButton = document.getElementById('save-settings');
    const toggleRulesButton = document.getElementById('toggle-rules');
    const resetButton = document.getElementById('reset-game');

    // Game elements
    const checkersBoard = document.getElementById('checkers-board');
    const currentPlayerDisplay = document.getElementById('current-player');
    const gameMessage = document.getElementById('game-message');
    const rulesContent = document.getElementById('rules-content');

    // Settings elements
    const flyingKingsCheckbox = document.getElementById('flying-kings');
    const backwardsCaptureCheckbox = document.getElementById('backwards-capture');
    const multipleCaptureCheckbox = document.getElementById('multiple-capture');
    const forceCaptureCheckbox = document.getElementById('force-capture');

    // Rules elements
    const ruleFlyingKings = document.getElementById('rule-flying-kings');
    const ruleBackwardsCapture = document.getElementById('rule-backwards-capture');
    const ruleMultipleCapture = document.getElementById('rule-multiple-capture');
    const ruleForceCaptue = document.getElementById('rule-force-capture');

    // Game constants
    const BOARD_SIZE = 8;
    const EMPTY = 0;
    const RED = 1;
    const BLACK = 2;
    const RED_KING = 3;
    const BLACK_KING = 4;

    // Game state
    let board = [];
    let selectedPiece = null;
    let currentPlayer = RED; // Red starts
    let possibleMoves = [];
    let mustJump = false;
    let gameOver = false;

    // Game settings
    let settings = {
        flyingKings: true,
        backwardsCapture: true,
        multipleCapture: true,
        forceCapture: true
    };

    // Load settings from localStorage if available
    function loadSettings() {
        const savedSettings = localStorage.getItem('checkersSettings');
        if (savedSettings) {
            settings = JSON.parse(savedSettings);

            // Update checkboxes to match saved settings
            flyingKingsCheckbox.checked = settings.flyingKings;
            backwardsCaptureCheckbox.checked = settings.backwardsCapture;
            multipleCaptureCheckbox.checked = settings.multipleCapture;
            forceCaptureCheckbox.checked = settings.forceCapture;
        }

        updateRulesDisplay();
    }

    // Save settings to localStorage
    function saveSettings() {
        settings.flyingKings = flyingKingsCheckbox.checked;
        settings.backwardsCapture = backwardsCaptureCheckbox.checked;
        settings.multipleCapture = multipleCaptureCheckbox.checked;
        settings.forceCapture = forceCaptureCheckbox.checked;

        localStorage.setItem('checkersSettings', JSON.stringify(settings));
        updateRulesDisplay();

        // Show confirmation
        alert('Settings saved successfully!');
    }

    // Update rules display based on settings
    function updateRulesDisplay() {
        ruleFlyingKings.textContent = settings.flyingKings ?
            "Kings can move any distance diagonally if unobstructed" :
            "Kings can only move one square diagonally";

        ruleBackwardsCapture.textContent = settings.backwardsCapture ?
            "Regular pieces can capture backwards" :
            "Regular pieces cannot capture backwards";

        ruleMultipleCapture.textContent = settings.multipleCapture ?
            "Multiple jumps in a single turn are allowed and required when possible" :
            "Only one jump is allowed per turn";

        ruleForceCaptue.textContent = settings.forceCapture ?
            "If a jump is available, you must take it" :
            "Jumping is optional";
    }

    // Screen navigation functions
    function showHomeScreen() {
        console.log("Showing home screen");
        homeScreen.style.display = 'flex';
        settingsScreen.style.display = 'none';
        gameScreen.style.display = 'none';
        gameOver = true; // Stop the game when returning to home
    }

    function showSettingsScreen() {
        console.log("Showing settings screen");
        homeScreen.style.display = 'none';
        settingsScreen.style.display = 'flex';
        gameScreen.style.display = 'none';
    }

    function showGameScreen() {
        console.log("Showing game screen");
        homeScreen.style.display = 'none';
        settingsScreen.style.display = 'none';
        gameScreen.style.display = 'block'; // Changed to block instead of flex

        // Ensure the board is visible
        checkersBoard.style.display = 'grid';

        // Force a layout recalculation
        setTimeout(() => {
            resetGame(); // Start a new game when entering game screen
            console.log("Board initialized and rendered");
        }, 100);
    }

    // Create the board
    function initializeBoard() {
        board = [];

        // Initialize empty board
        for (let row = 0; row < BOARD_SIZE; row++) {
            board[row] = [];
            for (let col = 0; col < BOARD_SIZE; col++) {
                board[row][col] = EMPTY;
            }
        }

        // Place pieces
        for (let row = 0; row < 3; row++) {
            for (let col = 0; col < BOARD_SIZE; col++) {
                if ((row + col) % 2 === 1) {
                    board[row][col] = BLACK;
                }
            }
        }

        for (let row = 5; row < 8; row++) {
            for (let col = 0; col < BOARD_SIZE; col++) {
                if ((row + col) % 2 === 1) {
                    board[row][col] = RED;
                }
            }
        }
    }

    // Render the board
    function renderBoard() {
        console.log("Rendering board...");

        // Ensure the board element exists
        if (!checkersBoard) {
            console.error("Checkers board element not found!");
            return;
        }

        // Clear the board
        checkersBoard.innerHTML = '';

        // Make sure the board is visible
        checkersBoard.style.display = 'grid';
        checkersBoard.style.gridTemplateColumns = 'repeat(8, 1fr)';
        checkersBoard.style.gridTemplateRows = 'repeat(8, 1fr)';
        checkersBoard.style.width = '100%';
        checkersBoard.style.maxWidth = '500px';
        checkersBoard.style.aspectRatio = '1/1';
        checkersBoard.style.margin = '0 auto';
        checkersBoard.style.border = '4px solid #472b1d';

        // Create all board squares
        for (let row = 0; row < BOARD_SIZE; row++) {
            for (let col = 0; col < BOARD_SIZE; col++) {
                const square = document.createElement('div');
                square.classList.add('board-square');
                square.classList.add((row + col) % 2 === 0 ? 'white' : 'black');
                square.dataset.row = row;
                square.dataset.col = col;

                // Add debug identifiers
                square.setAttribute('title', `Square ${row},${col}`);

                // Set minimum dimensions to ensure visibility
                square.style.minHeight = '30px';
                square.style.minWidth = '30px';

                if (board[row][col] !== EMPTY) {
                    const piece = document.createElement('div');
                    piece.classList.add('piece');

                    if (board[row][col] === RED || board[row][col] === RED_KING) {
                        piece.classList.add('red');
                    } else {
                        piece.classList.add('black');
                    }

                    if (board[row][col] === RED_KING || board[row][col] === BLACK_KING) {
                        piece.classList.add('king');
                    }

                    // Add selected class if this is the selected piece
                    if (selectedPiece && selectedPiece.row === row && selectedPiece.col === col) {
                        piece.classList.add('selected');
                    }

                    square.appendChild(piece);
                }

                square.addEventListener('click', handleSquareClick);
                checkersBoard.appendChild(square);
            }
        }

        // Highlight possible moves
        if (selectedPiece && possibleMoves.length > 0) {
            for (const move of possibleMoves) {
                const square = document.querySelector(`.board-square[data-row="${move.row}"][data-col="${move.col}"]`);
                if (square) {
                    square.classList.add('highlight');
                }
            }
        }

        // Update current player display
        currentPlayerDisplay.textContent = `Current Player: ${currentPlayer === RED ? 'Red' : 'Black'}`;
        currentPlayerDisplay.className = currentPlayer === RED ? 'me-3' : 'me-3 black';
    }

    // Handle clicking on a square
    function handleSquareClick(event) {
        if (gameOver) return;

        const square = event.currentTarget;
        const row = parseInt(square.dataset.row);
        const col = parseInt(square.dataset.col);

        // Check if player clicked on a possible move
        if (selectedPiece && possibleMoves.some(move => move.row === row && move.col === col)) {
            makeMove(row, col);
            return;
        }

        // Check if player clicked on their own piece
        if (
            (currentPlayer === RED && (board[row][col] === RED || board[row][col] === RED_KING)) ||
            (currentPlayer === BLACK && (board[row][col] === BLACK || board[row][col] === BLACK_KING))
        ) {
            // If force capture is enabled and there's a required jump, only allow selecting pieces that can jump
            if (settings.forceCapture && mustJump) {
                const jumpMoves = findPossibleMoves(row, col, true);
                if (jumpMoves.length === 0) {
                    return; // Can't select pieces that don't have jumps when jumps are required
                }
            }

            // Select the piece
            selectedPiece = { row, col };
            possibleMoves = settings.forceCapture ?
                findPossibleMoves(row, col, mustJump) :
                findPossibleMoves(row, col, false);

            renderBoard();
        }
    }

    // Find all possible moves for a piece
    function findPossibleMoves(row, col, jumpOnly = false) {
        const moves = [];
        const piece = board[row][col];

        // Check diagonal directions based on piece type
        const directions = [];

        // Regular pieces can only move forward
        if (piece === RED || piece === RED_KING) {
            directions.push({ row: -1, col: -1 }, { row: -1, col: 1 });
        }

        if (piece === BLACK || piece === BLACK_KING) {
            directions.push({ row: 1, col: -1 }, { row: 1, col: 1 });
        }

        // Kings can also move backward
        if (piece === RED_KING || piece === BLACK_KING) {
            if (piece === RED_KING) {
                directions.push({ row: 1, col: -1 }, { row: 1, col: 1 });
            } else {
                directions.push({ row: -1, col: -1 }, { row: -1, col: 1 });
            }
        }

        // Check for jumps (captures)
        const jumpMoves = [];

        // Include backward jump directions for regular pieces if backwardsCapture is enabled
        const jumpDirections = [...directions];
        if (settings.backwardsCapture) {
            if (piece === RED && !jumpDirections.some(d => d.row === 1)) {
                jumpDirections.push({ row: 1, col: -1 }, { row: 1, col: 1 });
            } else if (piece === BLACK && !jumpDirections.some(d => d.row === -1)) {
                jumpDirections.push({ row: -1, col: -1 }, { row: -1, col: 1 });
            }
        }

        // Check for jumps in all applicable directions
        for (const dir of jumpDirections) {
            const newRow = row + dir.row;
            const newCol = col + dir.col;

            // Check if the jump target is on the board
            if (newRow >= 0 && newRow < BOARD_SIZE && newCol >= 0 && newCol < BOARD_SIZE) {
                const targetPiece = board[newRow][newCol];

                // If there's an opponent's piece to jump over
                if (
                    (currentPlayer === RED && (targetPiece === BLACK || targetPiece === BLACK_KING)) ||
                    (currentPlayer === BLACK && (targetPiece === RED || targetPiece === RED_KING))
                ) {
                    const jumpRow = newRow + dir.row;
                    const jumpCol = newCol + dir.col;

                    // Check if the landing square is on the board and empty
                    if (
                        jumpRow >= 0 && jumpRow < BOARD_SIZE &&
                        jumpCol >= 0 && jumpCol < BOARD_SIZE &&
                        board[jumpRow][jumpCol] === EMPTY
                    ) {
                        jumpMoves.push({
                            row: jumpRow,
                            col: jumpCol,
                            isJump: true,
                            jumpedRow: newRow,
                            jumpedCol: newCol
                        });
                    }
                }
            }
        }

        // If there are jump moves or we're only looking for jumps, return them
        if (jumpMoves.length > 0 || jumpOnly) {
            return jumpMoves;
        }

        // Flying kings movement (move any distance)
        if (settings.flyingKings && (piece === RED_KING || piece === BLACK_KING)) {
            for (const dir of directions) {
                let newRow = row + dir.row;
                let newCol = col + dir.col;

                // Continue in the same direction until hitting a piece or edge
                while (
                    newRow >= 0 && newRow < BOARD_SIZE &&
                    newCol >= 0 && newCol < BOARD_SIZE
                ) {
                    if (board[newRow][newCol] === EMPTY) {
                        moves.push({
                            row: newRow,
                            col: newCol,
                            isJump: false
                        });

                        // Move further in the same direction
                        newRow += dir.row;
                        newCol += dir.col;
                    } else {
                        // Hit a piece, stop in this direction
                        break;
                    }
                }
            }
        } else {
            // Regular moves (non-jumps) for normal kings and regular pieces
            for (const dir of directions) {
                const newRow = row + dir.row;
                const newCol = col + dir.col;

                if (
                    newRow >= 0 && newRow < BOARD_SIZE &&
                    newCol >= 0 && newCol < BOARD_SIZE &&
                    board[newRow][newCol] === EMPTY
                ) {
                    moves.push({
                        row: newRow,
                        col: newCol,
                        isJump: false
                    });
                }
            }
        }

        return moves;
    }

    // Execute a move
    function makeMove(toRow, toCol) {
        const fromRow = selectedPiece.row;
        const fromCol = selectedPiece.col;
        const piece = board[fromRow][fromCol];

        // Find the chosen move from possible moves
        const move = possibleMoves.find(m => m.row === toRow && m.col === toCol);

        // Move the piece
        board[toRow][toCol] = piece;
        board[fromRow][fromCol] = EMPTY;

        // Check for king promotion
        if (piece === RED && toRow === 0) {
            board[toRow][toCol] = RED_KING;
        } else if (piece === BLACK && toRow === BOARD_SIZE - 1) {
            board[toRow][toCol] = BLACK_KING;
        }

        // Handle jump (capture)
        let canJumpAgain = false;
        if (move.isJump) {
            board[move.jumpedRow][move.jumpedCol] = EMPTY; // Remove jumped piece

            // Check if the piece can jump again from the new position (if multiple capture is enabled)
            if (settings.multipleCapture) {
                const additionalJumps = findPossibleMoves(toRow, toCol, true);
                if (additionalJumps.length > 0) {
                    canJumpAgain = true;
                    selectedPiece = { row: toRow, col: toCol };
                    possibleMoves = additionalJumps;
                }
            }
        }

        // Reset selection if the turn is over
        if (!canJumpAgain) {
            selectedPiece = null;
            possibleMoves = [];
            switchPlayer();
        }

        renderBoard();
        checkGameStatus();
    }

    // Switch to the next player
    function switchPlayer() {
        currentPlayer = currentPlayer === RED ? BLACK : RED;

        // Check if the new current player has any jumps available (only if force capture is enabled)
        mustJump = settings.forceCapture ? checkForAvailableJumps() : false;

        // If there are no valid moves, the current player loses
        if (!checkForAnyMoves()) {
            gameOver = true;
            gameMessage.textContent = `${currentPlayer === RED ? 'Black' : 'Red'} wins! No moves available.`;
            gameMessage.className = `mt-3 fs-5 fw-bold ${currentPlayer === RED ? 'black-wins' : 'red-wins'}`;
        }
    }

    // Check for any available jumps for the current player
    function checkForAvailableJumps() {
        for (let row = 0; row < BOARD_SIZE; row++) {
            for (let col = 0; col < BOARD_SIZE; col++) {
                const piece = board[row][col];
                if (
                    (currentPlayer === RED && (piece === RED || piece === RED_KING)) ||
                    (currentPlayer === BLACK && (piece === BLACK || piece === BLACK_KING))
                ) {
                    const jumpMoves = findPossibleMoves(row, col, true);
                    if (jumpMoves.length > 0) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    // Check if the current player has any valid moves
    function checkForAnyMoves() {
        for (let row = 0; row < BOARD_SIZE; row++) {
            for (let col = 0; col < BOARD_SIZE; col++) {
                const piece = board[row][col];
                if (
                    (currentPlayer === RED && (piece === RED || piece === RED_KING)) ||
                    (currentPlayer === BLACK && (piece === BLACK || piece === BLACK_KING))
                ) {
                    const moves = findPossibleMoves(row, col, false);
                    if (moves.length > 0) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    // Check if the game is over
    function checkGameStatus() {
        let redCount = 0;
        let blackCount = 0;

        for (let row = 0; row < BOARD_SIZE; row++) {
            for (let col = 0; col < BOARD_SIZE; col++) {
                const piece = board[row][col];
                if (piece === RED || piece === RED_KING) {
                    redCount++;
                } else if (piece === BLACK || piece === BLACK_KING) {
                    blackCount++;
                }
            }
        }

        if (redCount === 0) {
            gameOver = true;
            gameMessage.textContent = 'Black wins!';
            gameMessage.className = 'mt-3 fs-5 fw-bold black-wins';
        } else if (blackCount === 0) {
            gameOver = true;
            gameMessage.textContent = 'Red wins!';
            gameMessage.className = 'mt-3 fs-5 fw-bold red-wins';
        }
    }

    // Reset the game
    function resetGame() {
        gameOver = false;
        currentPlayer = RED;
        selectedPiece = null;
        possibleMoves = [];
        mustJump = settings.forceCapture ? checkForAvailableJumps() : false;
        gameMessage.textContent = '';
        gameMessage.className = 'mt-3 fs-5 fw-bold';

        initializeBoard();
        renderBoard();
    }

    // Toggle rules visibility
    function toggleRules() {
        if (rulesContent.style.display === 'none') {
            rulesContent.style.display = 'block';
        } else {
            rulesContent.style.display = 'none';
        }
    }

    // Add event listeners for all buttons
    if (playButton) {
        playButton.addEventListener('click', showGameScreen);
    }

    if (settingsButton) {
        settingsButton.addEventListener('click', showSettingsScreen);
    }

    if (backFromSettingsButton) {
        backFromSettingsButton.addEventListener('click', showHomeScreen);
    }

    if (backToHomeButton) {
        backToHomeButton.addEventListener('click', showHomeScreen);
    }

    if (saveSettingsButton) {
        saveSettingsButton.addEventListener('click', saveSettings);
    }

    if (resetButton) {
        resetButton.addEventListener('click', resetGame);
    }

    if (toggleRulesButton) {
        toggleRulesButton.addEventListener('click', toggleRules);
    }

    // Initialize the game
    console.log("Initializing checkers game...");

    // Initialize the board array first
    initializeBoard();

    // Load settings
    loadSettings();

    // Debug messages to check element existence
    console.log("Home screen element exists:", !!homeScreen);
    console.log("Settings screen element exists:", !!settingsScreen);
    console.log("Game screen element exists:", !!gameScreen);
    console.log("Checkers board element exists:", !!checkersBoard);

    // Initial visibility
    if (homeScreen) homeScreen.style.display = 'flex';
    if (settingsScreen) settingsScreen.style.display = 'none';
    if (gameScreen) gameScreen.style.display = 'none';

    // Show home screen by default
    showHomeScreen();
});