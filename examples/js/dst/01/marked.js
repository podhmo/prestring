const program = require("commander");
const fs = require("fs");
const marked = require("marked");

program
  .option("--gfm", "gfm mode is activated")
  .option("-S", "--sanitize", "sanitization");


program.parse(process.argv);
const filePath = program.args[0];

const markedOptions =  {
  gfm: false,
  sanitize: false,
  ...program.opts()
};

fs.readFile(filePath, {"encoding": "utf-8"}, (err, file) =>  {
  if (err) {
    console.error(err);
    process.exit(err.code);
    return;
  }
  const html = marked(file, {
    gfm: markedOptions.gfm,
    sanitize: markedOptions.sanitize
  });
  console.log(html);
});
