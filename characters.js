const priemGetallen = [];
const gettt = {};
for (let i = 2; i < 1000; i++) {
  const p = String.fromCharCode(i);
  gettt[p] = p;
  if (isPriem(i)) {
    priemGetallen.push(i);
  }
}
function isPriem(num) {
  for (let getal = 2; getal < num; getal++) {
    if (num % getal == 0) {
      return false;
    }
  }
  return true;
}
console.log(priemGetallen);
console.log(gettt);
