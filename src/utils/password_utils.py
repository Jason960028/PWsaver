# Password utilities for PwKeeper
# Includes password generation and strength checking

import random
import string
import re


class PasswordGenerator:
    """Secure password generator with customizable options"""

    @staticmethod
    def generate(length=16, use_uppercase=True, use_lowercase=True, use_numbers=True, use_symbols=True):
        """
        Generate a secure random password

        Args:
            length: Password length (default 16)
            use_uppercase: Include uppercase letters A-Z
            use_lowercase: Include lowercase letters a-z
            use_numbers: Include numbers 0-9
            use_symbols: Include special symbols

        Returns:
            Generated password string
        """
        if length < 4:
            length = 4  # Minimum length

        charset = ''
        password_chars = []

        # Build character set and ensure at least one of each enabled type
        if use_lowercase:
            charset += string.ascii_lowercase
            password_chars.append(random.choice(string.ascii_lowercase))

        if use_uppercase:
            charset += string.ascii_uppercase
            password_chars.append(random.choice(string.ascii_uppercase))

        if use_numbers:
            charset += string.digits
            password_chars.append(random.choice(string.digits))

        if use_symbols:
            symbols = '!@#$%^&*()-_=+[]{}|;:,.<>?'
            charset += symbols
            password_chars.append(random.choice(symbols))

        if not charset:
            # Fallback if nothing selected
            charset = string.ascii_letters + string.digits
            password_chars = []

        # Fill remaining length with random characters
        remaining_length = length - len(password_chars)
        for _ in range(remaining_length):
            password_chars.append(random.choice(charset))

        # Shuffle to avoid predictable patterns
        random.shuffle(password_chars)

        return ''.join(password_chars)


class PasswordStrengthChecker:
    """Password strength analyzer"""

    @staticmethod
    def check_strength(password):
        """
        Check password strength

        Args:
            password: Password string to analyze

        Returns:
            Tuple of (strength_level, score, suggestions)
            - strength_level: 'weak', 'medium', or 'strong'
            - score: 0-100
            - suggestions: List of improvement suggestions
        """
        if not password:
            return ('weak', 0, ['Password cannot be empty'])

        score = 0
        suggestions = []

        # Length check (0-30 points)
        length = len(password)
        if length < 6:
            score += length * 3
            suggestions.append('Use at least 8 characters (12+ recommended)')
        elif length < 8:
            score += 18
            suggestions.append('Use 12 or more characters for better security')
        elif length < 12:
            score += 25
        else:
            score += 30

        # Character variety (0-40 points)
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_numbers = bool(re.search(r'\d', password))
        has_symbols = bool(re.search(r'[^a-zA-Z0-9]', password))

        variety_count = sum([has_lowercase, has_uppercase, has_numbers, has_symbols])
        score += variety_count * 10

        if not has_lowercase and not has_uppercase:
            suggestions.append('Add letters to your password')
        elif not has_lowercase or not has_uppercase:
            suggestions.append('Mix uppercase and lowercase letters')

        if not has_numbers:
            suggestions.append('Add numbers to your password')

        if not has_symbols:
            suggestions.append('Add special symbols (!@#$%^&*...)')

        # Patterns and common weaknesses (0-30 points)
        weakness_penalty = 0

        # Check for repeated characters (aaa, 111, etc.)
        if re.search(r'(.)\1{2,}', password):
            weakness_penalty += 10
            suggestions.append('Avoid repeating characters')

        # Check for sequential patterns (abc, 123, etc.)
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            weakness_penalty += 10
            suggestions.append('Avoid sequential letters (abc, xyz)')

        if re.search(r'(012|123|234|345|456|567|678|789)', password):
            weakness_penalty += 10
            suggestions.append('Avoid sequential numbers (123, 456)')

        # Check for common patterns
        common_patterns = ['password', 'admin', 'user', 'login', '12345', 'qwerty']
        password_lower = password.lower()
        for pattern in common_patterns:
            if pattern in password_lower:
                weakness_penalty += 15
                suggestions.append('Avoid common words and patterns')
                break

        # Apply weakness penalty
        score = max(0, score - weakness_penalty)

        # Bonus for good length with variety
        if length >= 12 and variety_count >= 3:
            score += 10

        if length >= 16 and variety_count == 4:
            score += 10

        # Cap score at 100
        score = min(100, score)

        # Determine strength level
        if score < 40:
            strength = 'weak'
        elif score < 70:
            strength = 'medium'
        else:
            strength = 'strong'

        # Add general suggestion if no specific ones
        if not suggestions:
            if strength == 'medium':
                suggestions.append('Good password! Consider making it longer.')
            elif strength == 'strong':
                suggestions.append('Excellent password!')

        return (strength, score, suggestions)

    @staticmethod
    def get_strength_color(strength):
        """Get color code for strength level"""
        colors = {
            'weak': '#ef4444',      # Red
            'medium': '#f59e0b',    # Amber
            'strong': '#10b981'     # Green
        }
        return colors.get(strength, '#9ca3af')

    @staticmethod
    def get_strength_text(strength):
        """Get display text for strength level"""
        texts = {
            'weak': 'Weak',
            'medium': 'Medium',
            'strong': 'Strong'
        }
        return texts.get(strength, 'Unknown')
