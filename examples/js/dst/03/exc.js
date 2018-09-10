try {
  // throw custom exception;
  throw new Error('error');
} catch (error) {
  console.log(error.message); // error is thrown
}

function assertPositiveNumber(num) {
  if (num) {
    throw new Error(`${num} is not positive`);
  }
}


for (let i=0; i<10; i++) {
  console.log(i);
}
