class ArrayLike {
  constructor(items=[]) {
    this._items = items;
  }

  get items() {
    return this._items;
  }

  set items(newLength) {
    const currentItemLength = this.items.length;
    if (newLength < currentItemLength) {
      this._items = this.items.slice(0, newLength);
    }
    else if (newLength > currentItemLength) {
      this._items = this.items.concat(new Array(newLength - currentItemLength));
    }
  }

}

const arrayLike = new ArrayLike([1, 2, 3, 4, 5]);

arrayLike.length = 2;
console.log(arrayLike.items.join(', ')); // => '1, 2'

arrayLike.length = 5;
console.log(arrayLike.items.join(', ')); // => '1, 2, , ,'
class ArrayWrapper {
  consutructor(array=[]) {
    this.array = array;
  }

  static of(...items) {
    return new ArrayWrapper(items);
  }

  get length() {
    return this.array.length;
  }

}

arrayWrapperA = new ArrayWrapper([1, 2, 3]);

arrayWrapperB = ArrayWrapper.of(1, 2, 3);
console.log(arrayWrapperA.length); // => 3
console.log(arrayWrapperB.length); // => 3

class MyArray extends Array {
  get first() {
    if (this.length === 0) {
      return undefined;
    }
    else {
      return this[0];
    }
  }

  get last() {
    if (this.length === 0) {
      return undefined;
    }
    else {
      return this[this.length - 1];
    }
  }

}
