function orderDiacritics(input) {
    const combiningMacron = '\u0304'; // Combining Macron
    const combiningBreve = '\u0306'; // Combining Breve
    const baseAlphabet = /[ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρσςτυφχψω]/; // Greek base alphabet

    function decomposeCharacter(ch) {
        return ch.normalize('NFD');
    }

    function composeCharacter(baseChar, combiningMark, otherDiacritics) {
        return baseChar + combiningMark + otherDiacritics;
    }

    let output = '';

    for (const char of input) {
        const decomposed = decomposeCharacter(char);
        let baseChar = '';
        let combiningMark = '';
        let otherDiacritics = '';

        // Find the base character and separate combining marks
        for (const component of decomposed) {
            if (baseAlphabet.test(component)) {
                baseChar = component;
            } else if (component === combiningMacron || component === combiningBreve) {
                combiningMark = component;
            } else {
                otherDiacritics += component;
            }
        }

        // Compose the character in the desired order
        if (baseChar && combiningMark) {
            const baseMacronized = composeCharacter(baseChar, combiningMark, '');
            output += composeCharacter(baseMacronized, '', otherDiacritics);
        } else {
            output += char; // If no diacritics to reorder, keep the character as is
        }
    }

    return output;
}

// Example usage
const inputText = 'Ἀ̄γλά̆ῐσμᾰ'; // Example with combining diacritics
const outputText = orderDiacritics(inputText);
console.log(outputText);
