export function all(...iter: any[]) {
  for (let i of iter) {
    if (!i) {
      return false;
    }
  }
  return true;
}

export function flatten<T extends unknown>(arr: any[][]): T[] {
  return arr.reduce(function (flat, toFlatten) {
    return flat.concat(Array.isArray(toFlatten) ? flatten(toFlatten) : toFlatten);
  }, []);
}
