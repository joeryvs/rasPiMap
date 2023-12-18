
main();
const arr = []
arr.push(55358)
arr.push(55358);
// const u = String.fromCodePoint(arr);
const u = String.fromCodePoint(55358,55358,65,66,67)
console.log(u)
const q = String.fromCharCode(55358,55358,65,66,67);
console.log(q);


function main() {
    const line= "🍏 🍎 🍐 🍊 🍋 🍌 🍉 🍇 🍓 🫐 🍈 🍒 🍑 🥭 🍍 🥥 🥝 🍅 🍆 🥑 🥦 🥬 🥒 🌶 🫑 🌽 🥕 🫒 🧄 🧅 🥔";
    const tr = {};
    for (const iterator of line) {
        // if (iterator != ' ') {
            const temp = {len :0};
            temp.len = iterator.length;
            for (let i = 0; i < temp.len; i++){
                temp[i] = iterator.charCodeAt(0);
            }
            tr[iterator] = temp;
        // }
    }
    console.log(line.length)
    console.log(tr);
    
}