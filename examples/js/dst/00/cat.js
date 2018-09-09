const program = require("commander");
const fs = require("fs");

program.parse(process.argv);
const filePath = program.args[0];

fs.readFile(filePath, {"encoding": "utf-8"}, (err, file) =>  {
  if (err) {
    console.error(err);
    process.exit(err.code);
    return;
  }
  console.log(file);
});
