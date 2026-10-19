'use strict';
// One-shot generated-pigment transfer. Reads/writes only named workspace files.
const fs=require('node:fs'),crypto=require('node:crypto');
const {decodePNG,encodePNG,preview}=require('./finish_wall.js');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const source='artifacts/line-1/wall-v18.png',destination='artifacts/line-1/wall-v19.png';
if(fs.existsSync('dist/line-1/37.json')) throw Error('record already exists');
const raw=fs.readFileSync(source),ancestor=decodePNG(source);
const donorRaw=fs.readFileSync(destination),donor=decodePNG(destination);
if(JSON.parse(fs.readFileSync('dist/line-1/36.json')).image!=='https://api.imd.fun/artifacts/'+hash(raw)) throw Error('ancestor pin mismatch');
if(!raw.equals(fs.readFileSync('artifacts/line-1/wall.png'))) throw Error('current ancestor mismatch');
if(ancestor.width!==1254||ancestor.height!==1254||ancestor.channels!==3||donor.width!==1254||donor.height!==1254) throw Error('unexpected image');
const out={...ancestor,pixels:Buffer.from(ancestor.pixels)},bounds=[240,160,385,214];
let charcoal=0,chalk=0,ochre=0;
for(let y=bounds[1];y<bounds[3];y++) for(let x=bounds[0];x<bounds[2];x++) {
 const a=(y*ancestor.width+x)*3,d=(y*donor.width+x)*donor.channels;
 const [r,g,b]=donor.pixels.subarray(d,d+3),[ar,ag,ab]=ancestor.pixels.subarray(a,a+3);
 const dark=r<100&&g<85&&b<65&&ar-r>16&&ag-g>12;
 const light=r>145&&g>120&&b>90&&r-g<60&&g-ag>18&&b-ab>18;
 const red=r>125&&r-g>48&&g-b>15&&r-ar>12&&r-g>ar-ag+12;
 if(!dark&&!light&&!red) continue;
 const feather=Math.min(1,(x-bounds[0])/3,(bounds[2]-1-x)/3,(y-bounds[1])/3,(bounds[3]-1-y)/3);
 if(feather<=0) continue;
 const alpha=.85*feather;
 for(let c=0;c<3;c++) out.pixels[a+c]=Math.round(ancestor.pixels[a+c]*(1-alpha)+donor.pixels[d+c]*alpha);
 if(dark)charcoal++;else if(light)chalk++;else ochre++;
}
let changed=0;
for(let y=0;y<out.height;y++) for(let x=0;x<out.width;x++) {
 const i=(y*out.width+x)*3;
 if(!out.pixels.subarray(i,i+3).equals(ancestor.pixels.subarray(i,i+3))) {
  changed++;
  if(x<bounds[0]||x>=bounds[2]||y<bounds[1]||y>=bounds[3]) throw Error('outside mutation');
 }
}
if(charcoal<100||chalk<100||ochre<30) throw Error('missing pigment');
const png=encodePNG(out),jpg=preview(out),digest=hash(png);
if(jpg.length>100000)throw Error('preview too large');
fs.writeFileSync(destination,png);fs.writeFileSync('artifacts/line-1/wall.png',png);
fs.writeFileSync('dist/line-1/37.jpg',jpg);
fs.writeFileSync('dist/line-1/37.json',JSON.stringify({name:'A Place Kept Open',image:'https://api.imd.fun/artifacts/'+digest,attributes:[
 {trait_type:'Cave',value:'Roots'},{trait_type:'Wall',value:'Line 1'},{trait_type:'Number',value:37},
 {trait_type:'Left behind',value:'Roster Bounds'},
 {trait_type:'Meaning',value:'A chalk cradle keeps an open ochre place beside charcoal pebbles so no planned case disappears.'},
 {trait_type:'One thing',value:'Reproducible benchmark evidence'}]},null,2)+'\n');
const review={wall:destination,width:1254,height:1254,format:'PNG RGB8',bytes:png.length,sha256:digest,
 preview:{path:'dist/line-1/37.jpg',width:512,height:512,format:'JPEG',bytes:jpg.length},
 ancestor:source,ancestor_sha256:hash(raw),generated_image_sha256:hash(donorRaw),bounds,changed_pixels:changed,
 charcoal_pixels:charcoal,chalk_pixels:chalk,ochre_pixels:ochre,all_pixels_outside_bounds_identical:true,
 process:'Built-in image generator edited the inherited wall. Only new charcoal, chalk and ochre pigment in bare upper-left rock was transferred. Generated intermediate overwritten by the finished whole wall.',
 visual_review:{status:'pending inspection',unmet_visual_requirements:[]},
 preview_location_exception:'The assignment explicitly requires the numbered JPEG beside its JSON in dist/line-1.'};
fs.writeFileSync('line-1/wall-review-37.json',JSON.stringify(review,null,2)+'\n');
console.log(JSON.stringify(review));
