function isPriem(num) {
  for (let getal = 2; getal < num; getal++) {
    if (num % getal == 0) {
      return false;
    }
  }
  return true;
}

function priemLoop(params) {
  const priemGetallen = [];
  for (let i = 2; i < params; i++) {
    if (isPriem(i)) {
      priemGetallen.push(i);
    }
  }
  return priemGetallen;
}

const pr = priemLoop(4000);
console.log(pr);
