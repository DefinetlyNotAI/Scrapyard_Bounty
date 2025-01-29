// Generate random binary code in the background
function generateErrorCode() {
    const errorCode = document.querySelector('.error-code');
    setInterval(() => {
        errorCode.textContent = Array.from({length: 8}, () =>
            Math.random() > 0.5 ? '1' : '0'
        ).join('');
    }, 100);
}

// Simulate retry connection with loading state
function retryConnection() {
    const btn = document.querySelector('.retry-btn');
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Retrying...';

    // Add more glitch effect during retry
    document.querySelector('.server').style.animation = 'server-shake 0.2s ease-in-out infinite';

    setTimeout(() => {
        btn.disabled = false;
        btn.textContent = originalText;
        document.querySelector('.server').style.animation = 'server-shake 0.5s ease-in-out infinite';

        // Attempt to refresh the page
        // FIXME refresh ignore the below code
        location.reload();

        // Show a random error message if refresh fails
        setTimeout(() => {
            const errorMessages = [
                "Critical system failure: Too many cats in the database!",
                "Error 500: Server turned into a toaster",
                "Quantum fluctuation detected in the coffee machine",
                "Server.exe has stopped working... and started dancing",
                "Emergency: CPU needs a vacation!",
                "System.out.of.cheese.error",
                "HTTP 500: Server is having an existential crisis",
                "Well this is embarrassing... Server is on strike",
                "Server is on fire, send a Halo-carbon fire extinguishers",
                "Server is busy playing Minecraft",
                "Server is too busy watching cat videos",
                "Server is feeling a bit under the weather",
            ];

            const errorDetails = [
                "MAXIMUM_CALL_STACK_SIZE_EXCEEDED",
                "UNEXPECTED_TOKEN_UNICORN",
                "NULL_POINTER_EXCEPTION",
                "DIVISION_BY_ZERO",
                "MEMORY_OVERFLOW",
                "SYNTAX_ERROR_EXPECTED_SEMICOLON_GOT_PIZZA",
            ];

            document.querySelector('.description').textContent =
                errorMessages[Math.floor(Math.random() * errorMessages.length)];

            document.querySelector('.error-details').innerHTML =
                `<span>Error: INTERNAL_SERVER_ERROR</span><br>
                 <span>Status: 500</span><br>
                 <span>Stack: ${errorDetails[Math.floor(Math.random() * errorDetails.length)]}</span>`;
        }, 2000);
    }, 2000);
}

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    generateErrorCode();
});