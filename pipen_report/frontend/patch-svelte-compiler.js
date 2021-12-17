/*
  Patch svelte compiler to fix
  "Max Stack Size Exceeded for huge HTML"
  https://github.com/sveltejs/svelte/issues/4694

  All credits to @milahu
  https://github.com/sveltejs/svelte/issues/4694#issuecomment-637434624

  To run:
  > make patch
*/

// TODO chose your package type from package.json
// TODO patch both js and mjs files
var base_file = "compiler.js"; // "type": "commonjs"
//var base_file = "compiler.mjs"; // "type": "module" // TODO verify

const input_file = base_file + ".orig";
const output_file = base_file + ".new";

// replaceMethod
//   origin: a.push(...a1, ...a2, e, ...a3); // error: Max Stack Size Exceeded
//   spread: a = [...a1, ...a2, e, ...a3];
//   concat: a = a1.concat(a2, [e], a3);
//   performance is equal on nodejs
const replaceMethod = "spread";
//const replaceMethod = "concat";

const acorn_parse = require("acorn").parse;
const estree_walk = require("estree-walker").walk;
const magicString = require("magic-string");
const fs = require("fs");

if (fs.existsSync(input_file) || fs.existsSync(output_file)) {
  console.log('error: input or output file exists. run this script only once');
  process.exit(1);
}

console.log(`move file: ${base_file} --> ${input_file}`)
fs.renameSync(base_file, input_file);

// input
const content = fs.readFileSync(input_file, 'utf8');

// output
let code = new magicString(content);

const ast = acorn_parse(
  content, {
  // ecmaVersion: 10, // default in year 2019
  sourceType: 'module',
});

const funcName = "push";

let arrayNameList = [];

estree_walk( ast, {
  enter: function ( node, parent, prop, index ) {

    // node must be array.push()
    if (
      node.type !== 'CallExpression' ||
      node.callee === undefined ||
      node.callee.property === undefined ||
      node.callee.property.name !== funcName
    ) { return; }

    // argument list must include spread operators
    if (node.arguments.find(
      a => (a.type == 'SpreadElement')) === undefined)
    { return; }

    const nodeSrc = content.substring(node.start, node.end);

    const pushObj = node.callee.object;
    const arrayName = content.substring(pushObj.start, pushObj.end);

    const pushProp = node.callee.property;

    arrayNameList.push(arrayName);

    // patch .push(

    if (replaceMethod == "spread") {
      // push --> assign array

      // find "(" bracket after .push
      const pushPropLen = content.substring(pushProp.start, node.end).indexOf("(");

      code.overwrite(
        (pushProp.start - 1),
        (pushProp.start + pushPropLen + 1),
        " /* PATCHED */ = [..."+arrayName+", "
      );

      // patch closing bracket
      const closeIdx = node.start + nodeSrc.lastIndexOf(")");
      code.overwrite(closeIdx, (closeIdx + 1), "]");
    }

    if (replaceMethod == "concat") {
      // push --> assign concat
      // ".push" --> " = array.concat"
      code.overwrite(
        (pushProp.start - 1),
        pushProp.end,
        " /* PATCHED */ = "+arrayName+".concat");

      // patch arguments of .concat()
      node.arguments.forEach(a => {
        if (a.type == 'SpreadElement') {
          // unspread: ...array --> array
          const spreadArgSrc = content.substring(a.argument.start, a.argument.end);
          //console.log('spread argument: '+spreadArgSrc);
          code.overwrite(a.start, a.end, spreadArgSrc);

        } else {
          // enlist: element --> [element]
          const argSrc = content.substring(a.start, a.end);
          //console.log('non spread argument: '+argSrc);
          code.overwrite(a.start, a.end, "["+argSrc+"]");
        }
      });
    }

}});

code = code.toString();

function filterUnique(value, index, array) {
  return array.indexOf(value) === index;
}

// replace const with let
arrayNameList.filter(filterUnique).forEach(arrayName => {
  console.log(`arrayName = ${arrayName}`)

  code = code.replace(
    new RegExp("const "+arrayName+" = ", 'g'), // global = replace all
    "/* PATCHED const "+arrayName+" */ let "+arrayName+" = "
  );
})

fs.writeFileSync(output_file, code);

console.log(`move file: ${output_file} --> ${base_file}`)
fs.renameSync(output_file, base_file);
