document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.getElementById('password');
    const passwordStrengthMessage = document.getElementById('password-strength');

    passwordInput.addEventListener('input', function () {
        const password = passwordInput.value;
        const isStrongPassword = checkPasswordStrength(password);

        if (isStrongPassword) {
            passwordStrengthMessage.style.display = 'none';
        } else {
            passwordStrengthMessage.style.display = 'block';
        }
    });

    function checkPasswordStrength(password) {
        // Define a regular expression to check for password strength
        const strongPasswordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        return strongPasswordRegex.test(password);
    }
});
