// Renderiza el SVG del isotipo ONCONOVA a PNG (verificacion / export rapido).
// Requiere: npm install @resvg/resvg-js
const fs = require('fs');
const path = require('path');
const { Resvg } = require('@resvg/resvg-js');

const dir = path.join(__dirname, '..');  // imagenes/branding
const svg = fs.readFileSync(path.join(dir, 'onconova_isotipo.svg'), 'utf8');
const r = new Resvg(svg, { fitTo: { mode: 'width', value: 600 } });
const png = r.render().asPng();
fs.writeFileSync(path.join(__dirname, '_svg_check.png'), png);
console.log('rendered', png.length, 'bytes ->', path.join(__dirname, '_svg_check.png'));
