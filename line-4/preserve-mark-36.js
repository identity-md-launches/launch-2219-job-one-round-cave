// One-time transfer of generated mineral pigment onto the inherited RGB8 wall.
// The generated donor temporarily occupies the required wall-v19.png path.
const fs = require('fs');
const zlib = require('zlib');
const crypto = require('crypto');

function decode(data) {
  if (data.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a') throw Error('PNG signature');
  let pos = 8, idat = [], width, height;
  while (pos < data.length) {
    const n = data.readUInt32BE(pos), kind = data.toString('ascii', pos + 4, pos + 8);
    const payload = data.subarray(pos + 8, pos + 8 + n);
    if (kind === 'IHDR') {
      width = payload.readUInt32BE(0); height = payload.readUInt32BE(4);
      if (payload[8] !== 8 || payload[9] !== 2 || payload[12] !== 0) throw Error('RGB8 noninterlaced required');
    }
    if (kind === 'IDAT') idat.push(payload);
    pos += n + 12;
    if (kind === 'IEND') break;
  }
  if (width !== 1254 || height !== 1254) throw Error('wall dimensions');
  const raw = zlib.inflateSync(Buffer.concat(idat));
  const stride = width * 3, pixels = Buffer.alloc(width * height * 3);
  if (raw.length !== (stride + 1) * height) throw Error('scanline size');
  for (let y = 0; y < height; y++) {
    const mode = raw[y * (stride + 1)];
    for (let x = 0; x < stride; x++) {
      const k = y * stride + x;
      const a = x >= 3 ? pixels[k - 3] : 0;
      const b = y ? pixels[k - stride] : 0;
      const c = y && x >= 3 ? pixels[k - stride - 3] : 0;
      let p = 0;
      if (mode === 1) p = a;
      else if (mode === 2) p = b;
      else if (mode === 3) p = Math.floor((a + b) / 2);
      else if (mode === 4) {
        const v = a + b - c, da = Math.abs(v - a), db = Math.abs(v - b), dc = Math.abs(v - c);
        p = da <= db && da <= dc ? a : db <= dc ? b : c;
      } else if (mode !== 0) throw Error('PNG filter');
      pixels[k] = (raw[y * (stride + 1) + 1 + x] + p) & 255;
    }
  }
  return {width, height, pixels};
}

function crc(data) {
  let c = 0xffffffff;
  for (const b of data) {
    c ^= b;
    for (let j = 0; j < 8; j++) c = (c >>> 1) ^ ((c & 1) ? 0xedb88320 : 0);
  }
  return (c ^ 0xffffffff) >>> 0;
}
function chunk(name, data) {
  const kind = Buffer.from(name), out = Buffer.alloc(data.length + 12);
  out.writeUInt32BE(data.length, 0); kind.copy(out, 4); data.copy(out, 8);
  out.writeUInt32BE(crc(Buffer.concat([kind, data])), data.length + 8);
  return out;
}
function encode(img) {
  const header = Buffer.alloc(13); header.writeUInt32BE(img.width, 0); header.writeUInt32BE(img.height, 4);
  header[8] = 8; header[9] = 2;
  const stride = img.width * 3, raw = Buffer.alloc((stride + 1) * img.height);
  for (let y = 0; y < img.height; y++) img.pixels.copy(raw, y * (stride + 1) + 1, y * stride, (y + 1) * stride);
  return Buffer.concat([Buffer.from('89504e470d0a1a0a', 'hex'), chunk('IHDR', header),
    chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
}

const ancestorPath = 'artifacts/line-4/wall-v18.png';
const targetPath = 'artifacts/line-4/wall-v19.png';
const ancestorBytes = fs.readFileSync(ancestorPath), donorBytes = fs.readFileSync(targetPath);
const ancestor = decode(ancestorBytes), donor = decode(donorBytes);
const donorHash = crypto.createHash('sha256').update(donorBytes).digest('hex');
const box = [887, 426, 1050, 486];
let changed = 0, bbox = [1254, 1254, 0, 0];
for (let y = box[1]; y < box[3]; y++) for (let x = box[0]; x < box[2]; x++) {
  const left = ((x - 902) / 22) ** 2 + ((y - 450) / 23) ** 2 < 1;
  const right = ((x - 1028) / 22) ** 2 + ((y - 450) / 23) ** 2 < 1;
  const middle = ((x - 968) / 23) ** 2 + ((y - 475) / 20) ** 2 < 1;
  const cordY = 450 + 26 * Math.sin(Math.PI * (x - 902) / 126);
  const cord = x >= 902 && x <= 1028 && Math.abs(y - cordY) < 12;
  if (!(left || right || middle || cord)) continue;
  const k = (y * 1254 + x) * 3;
  const difference = Math.max(...[0, 1, 2].map(c => Math.abs(donor.pixels[k + c] - ancestor.pixels[k + c])));
  if (difference <= 23) continue;
  donor.pixels.copy(ancestor.pixels, k, k, k + 3);
  changed++;
  bbox = [Math.min(bbox[0], x), Math.min(bbox[1], y), Math.max(bbox[2], x), Math.max(bbox[3], y)];
}
if (changed < 1000 || changed > 10000) throw Error('unexpected pigment pixel count: ' + changed);
const finalBytes = encode(ancestor);
fs.writeFileSync(targetPath, finalBytes);
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const process = {
  method: 'Generated mineral pigment transferred only inside a narrow bare-rock mask; all other ancestor pixels retained.',
  ancestor: ancestorPath, ancestor_sha256: hash(ancestorBytes),
  donor_sha256: donorHash, donor_box_xyxy_exclusive: box,
  difference_threshold: 23, changed_pixels: changed, changed_bbox_xyxy_inclusive: bbox,
  final_sha256: hash(finalBytes), preservation: 'Every pixel outside selected pigment is byte-identical after PNG decoding.'
};
fs.writeFileSync('line-4/mark-36-process.json', JSON.stringify(process, null, 2) + '\n');
console.log(JSON.stringify({changed, bbox, final_sha256: process.final_sha256}));
