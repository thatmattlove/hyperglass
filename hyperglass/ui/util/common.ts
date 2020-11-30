export function all(...iter: any[]) {
  for (let i of iter) {
    if (!i) {
      return false;
    }
  }
  return true;
}
