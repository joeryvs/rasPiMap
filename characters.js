function charrs(maxVal) {
  const gettt = {};
  const reverse = {};
  for (let i = 0; i < maxVal; i++) {
    const p = String.fromCharCode(i);
    gettt[p] = i;
    reverse[i] = p;
  }
  return gettt + reverse;
}

const b = charrs(400);

console.log(b);
