const program = require("commander");
const fs = require("fs");

program.parse(process.argv);
const filePath = program.args[0];

fs.readFile(filePath, (err, "utf8", file) =>  {
  console.log(file);
  if err {
    console.error(err);
    process.exit(err.code);
    return;
  }
  console.log(file);
});
