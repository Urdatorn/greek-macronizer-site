let currentIndex = -1; // Index for the currently highlighted suggestion

// Greek alphabet regex
const baseAlphabet = /[ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρσςτυφχψω]/;

// Function to get the base character after normalization
function base(ch) {
    return ch.normalize('NFD')[0];
}

// Function to apply diacritical marks based on instructions
import { reverseMacronsMap, reverseVrachysMap } from './maps.js';

function applyDiacritics(input, instructions) {
    const combiningMacron = '\u0304'; // Combining Macron
    const combiningBreve = '\u0306'; // Combining Breve

    // Split the instructions into pairs
    const instructionsArray = instructions.match(/[_^]\d+/g);
    if (!instructionsArray) return input; // No instructions

    // Filter Greek alphabet characters from the input
    let filteredInput = Array.from(input).filter(char => baseAlphabet.test(base(char)));

    // Apply diacritical marks based on the instructions
    for (const instruction of instructionsArray) {
        const type = instruction[0]; // '_' or '^'
        const index = parseInt(instruction.slice(1), 10) - 1; // Convert to 0-based index

        if (index >= 0 && index < filteredInput.length) {
            const currentChar = filteredInput[index];
            
            if (type === '_') {
                // Check reverseMacronsMap first
                if (reverseMacronsMap[currentChar]) {
                    filteredInput[index] = reverseMacronsMap[currentChar];
                } else {
                    // Combine with Macron
                    filteredInput[index] += combiningMacron;
                }
            } else if (type === '^') {
                // Check reverseVrachysMap first
                if (reverseVrachysMap[currentChar]) {
                    filteredInput[index] = reverseVrachysMap[currentChar];
                } else {
                    // Combine with Breve
                    filteredInput[index] += combiningBreve;
                }
            }
        }
    }

    return filteredInput.join('');
}

// Function to show suggestions as user types
document.getElementById('searchBox').addEventListener('input', async function () {
    const searchValue = this.value.trim().toLowerCase();
    const suggestionsBox = document.getElementById('suggestions');
    suggestionsBox.innerHTML = ''; // Clear previous suggestions
    currentIndex = -1; // Reset current index

    if (searchValue.length > 0) {
        const response = await fetch('macrons_alg4_barytone.tsv');
        const tsvData = await response.text();
        const lines = tsvData.split('\n').slice(1); // Skip the header

        const matches = lines.filter(line => {
            const columns = line.split('\t');
            const name = columns[0].trim().toLowerCase();
            return name.startsWith(searchValue);
        }).slice(0, 10); // Limit to top 10 matches

        matches.forEach(match => {
            const columns = match.split('\t');
            const name = columns[0].trim();
            const resultCol = columns[3];
            const sourceCol = columns[4].trim();

            const suggestionItem = document.createElement('div');
            suggestionItem.classList.add('suggestion-item');
            suggestionItem.innerHTML = `<strong>${name}</strong>: ${resultCol}<br>(Source: ${sourceCol})`;

            // On click, set the input value and hide suggestions
            suggestionItem.addEventListener('click', function () {
                document.getElementById('searchBox').value = name;
                suggestionsBox.innerHTML = '';
                searchTSV();
            });

            suggestionsBox.appendChild(suggestionItem);
        });
    }
});

// Event listener to handle keyboard navigation in suggestions
document.getElementById('searchBox').addEventListener('keydown', function (e) {
    const suggestionsBox = document.getElementById('suggestions');
    const items = suggestionsBox.getElementsByClassName('suggestion-item');

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (currentIndex < items.length - 1) {
            currentIndex++;
            updateHighlight(items);
        }
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (currentIndex > 0) {
            currentIndex--;
            updateHighlight(items);
        }
    } else if (e.key === 'Enter') {
        if (currentIndex > -1) {
            e.preventDefault();
            items[currentIndex].click();
        } else {
            e.preventDefault(); // Prevent the default form submission
            suggestionsBox.innerHTML = ''; // Clear the suggestions
            searchTSV(); // Perform the search
        }
    }
});

// Function to update the highlighted suggestion
function updateHighlight(items) {
    for (let i = 0; i < items.length; i++) {
        items[i].classList.remove('highlighted');
    }
    if (currentIndex > -1 && items[currentIndex]) {
        items[currentIndex].classList.add('highlighted');
    }
}

async function searchTSV() {
    const searchValue = document.getElementById('searchBox').value.trim();
    const response = await fetch('macrons_alg4_barytone.tsv');
    const tsvData = await response.text();

    const lines = tsvData.split('\n').slice(1); // Skip the header
    let result = "Not found";

    for (const line of lines) {
        const columns = line.split('\t');
        const name = columns[0].trim().toLowerCase();
        const resultCol = columns[3];
        let sourceCol = columns[4].trim();

        if (name === searchValue.trim().toLowerCase()) {
            if (sourceCol.toLowerCase() === 'breve_ultima') {
                sourceCol = 'Morphological tables for breve on the ultima';
            }
            // Apply diacritics based on the fourth column data
            const modifiedInput = applyDiacritics(searchValue, resultCol);
            result = `<span class="search-input">${modifiedInput}</span><br>${resultCol}<br>(Source: ${sourceCol})`;
            break;
        }
    }

    document.getElementById('result').innerHTML = result;
    document.getElementById('suggestions').innerHTML = ''; // Clear suggestions after the search
}

// Array of title options
const titles = [
    "σύστελλε τὰ δίχρονα!",
    "ἔκτεινε τὰ δίχρονα!",
    "ἢ ἐκτετᾰμένᾰ ἢ σῠνεστᾰλμένᾰ ἔχω τὰ δίχρονα!",
    "αὐτόμᾰτον ἐκτετᾰκὸς καὶ σῠνεστᾰλκός"
];

// Function to select a random title
function getRandomTitle() {
    const randomIndex = Math.floor(Math.random() * titles.length);
    return titles[randomIndex];
}

// Set the random title as the content of the h1 element
document.getElementById('title').innerText = getRandomTitle();

// Function to handle manual formatting input
document.getElementById('manualSearchBox').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
        e.preventDefault(); // Prevent default form submission
        const input = this.value.trim();
        const [text, instructions] = input.split(/\s(.+)/); // Split at the first space

        if (text && instructions) {
            const formattedText = applyDiacritics(text, instructions);
            document.getElementById('manualResult').innerHTML = `<span class="search-input">${formattedText}</span>`;
        } else {
            document.getElementById('manualResult').innerHTML = ''; // Clear result if input is not valid
        }
    }
});

// Function to copy text to clipboard
function copyToClipboard(text) {
    const tempInput = document.createElement("input");
    tempInput.style.position = "absolute";
    tempInput.style.left = "-9999px";
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand("copy");
    document.body.removeChild(tempInput);
}

// Add event listeners to all elements with the class 'search-input'
document.querySelectorAll('.search-input').forEach(element => {
    element.addEventListener('click', function() {
        copyToClipboard(this.textContent);
        alert(this.textContent + ' copied to clipboard!');
    });
});
