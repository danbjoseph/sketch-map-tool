var l=(a,c)=>{a||(a=".filebokz"),typeof c!="string"&&(c="filebokz");let d=["apng","bmp","gif","x-icon","jpeg","png","svg+xml","tiff","webp"],L=["kB","MB","GB","TB","PB","EB","ZB","YB"],A=document.createElement("div"),D="draggable"in A||"ondragstart"in A&&"ondrop"in A,Y="FormData"in window&&"FileReader"in window;l.count||(l.count=0),typeof a=="string"?a=document.querySelectorAll(a):a instanceof HTMLElement&&(a=[a]);let T=(t,e,s)=>{let n=t.querySelector(".error-msg"),r=t.dataset.errorDisplayDuration||3e3;t.classList.add("error");let f=t.dataset,o="";if(e==="maxFiles"&&(o=f.maxFilesErrorMsg||"A maximum of {variable} file{s} can be uploaded.",o=o.replace(/{variable}/ig,s),o=o.replace(/{s}/ig,s>1?"s":"")),e==="maxFileSize"&&(o=f.maxFileSizeErrorMsg||"File size cannot exceed {variable}.",o=o.replace(/{variable}/ig,k(s))),e==="maxSize"&&(o=f.maxSizeErrorMsg||"Total combined file size cannot exceed {variable}.",o=o.replace(/{variable}/ig,k(s))),e==="allowedExtensions"&&(o=f.allowedExtensionsErrorMsg||"Only the following file types are allowed: {variable}.",o=o.replace(/{variable}/ig,s)),n){n.innerHTML=o;let p=250;Object.prototype.hasOwnProperty.call(t.dataset,"errorAnimationDuration")&&(p=t.dataset.errorAnimationDuration),setTimeout(function(){n.innerHTML=""},r+p)}setTimeout(function(){t.classList.remove("error")},r),l.triggerEvent("error",t,{errorMessage:o,errorType:e})},I=(t,e,s,n)=>{if(Object.prototype.hasOwnProperty.call(t,e+n))return t[e+n];if(Object.prototype.hasOwnProperty.call(t,e+s))return t[e+s]},k=t=>{if(Math.abs(t)<1024)return t+" B";let e=-1;do t/=1024,++e;while(Math.round(Math.abs(t)*10)/10>=1024&&e<L.length-1);return+t.toFixed(1)+" "+L[e]},N=(t,e)=>{e.classList.remove("in-focus")},C=(t,e,s)=>{let n=s.files,r=s.originalFiles||[],f=t.filebokzAction==="remove";if(n.length){let i=!e.dataset.appendable||e.dataset.appendable.toLowerCase()!=="false",m=s.hasAttribute("multiple")&&s.getAttribute("multiple").toLowerCase()!=="false";if(i&&m&&!f&&r.length){let v=Array.from(n),b=Array.from(r);for(let u=0;u<v.length;u++){let M=!1;for(let g=0;g<b.length;g++)v[u].lastModifed===b[g].lastModifed&&v[u].name===b[g].name&&v[u].size===b[g].size&&v[u].type===b[g].type&&(M=!0);M||b.push(v[u])}s.files=l.newFileList(b),n=s.files}H(n,e,s)?e.classList.add("has-files"):n=[]}!n.length&&!f&&(s.files=l.newFileList(r),n=s.files),n.length||e.classList.remove("has-files"),s.originalFiles=n,e.dataset.fileCount=n.length;let o=e.querySelector(".file-count");o&&(o.innerHTML=n.length);let p=0;for(let i=0;i<n.length;i++)p+=n[i].size;e.dataset.size=p;let y=e.querySelector(".size");y&&(y.innerHTML=k(p));let w=e.querySelector(".files");if(w){let i=w.dataset,m=w.querySelectorAll(".file");if(m)for(let v=0;v<m.length;v++)w.removeChild(m[v]);if(n.length){let v=!i.draggable||i.draggable.toLowerCase()!=="false";for(let b=0;b<n.length;b++)(function(u,M){let g=u.type.split("/")[0],S=u.type.replace(/[/+-](\w{1})/g,function(F){return F.toUpperCase()}).replace(/[/+-]/g,"");g=g.charAt(0).toUpperCase()+g.slice(1);let j=I(i,"element",g,S);j=j||i.element||"span";let E=I(i,"content",g,S);E=E||i.content||"{name}";let P=I(i,"contentBefore",g,S);P=P||i.contentBefore||"";let q=I(i,"contentAfter",g,S);q=q||i.contentAfter||"";let O=I(i,"url",g,S);O||(d.includes(u.type.replace("image/",""))?O=window.URL.createObjectURL(u):O=i.url||""),E=P+E+q,E=E.replace(/{name}/ig,u.name),E=E.replace(/{type}/ig,u.type),E=E.replace(/{size}/ig,k(u.size)),E=E.replace(/{url}/ig,O);let h=document.createElement(j);h.className="file",h.innerHTML=E,D&&v&&(h.draggable="true",h.addEventListener("drag",function(F){K(F,e.id)},!1),h.addEventListener("dragstart",function(F){V(F,e.id)},!1));let R=h.querySelector(".remove");R&&R.addEventListener("click",function(F){X(F,s,M)},!1),w.append(h)})(n[b],b)}}n.length>r.length?l.triggerEvent("file-added",e):n.length<r.length&&l.triggerEvent("file-removed",e)},U=(t,e,s)=>{t.preventDefault(),t.stopPropagation(),e.classList.add("is-dragging")},G=(t,e)=>{t.preventDefault(),t.stopPropagation(),e.classList.remove("is-dragging")},W=(t,e,s)=>{t.preventDefault(),t.stopPropagation(),e.classList.remove("is-dragging");let n=t.dataTransfer.files,r=t.dataTransfer.getData("fileBoxId");if(r){let f=t.dataTransfer.getData("fileIndex"),o=document.getElementById(r),p=o.querySelector("input"),y=o.querySelector(".files").children[f];if(o.classList.remove("is-dragging"),o.classList.remove("is-removing"),o.classList.remove("is-transferring"),y.classList.remove("is-dragging"),y.classList.remove("is-removing"),y.classList.remove("is-transferring"),r===e.id)return;let w=Array.from(p.files),i=w[f],m=Array.from(s.files);s.hasAttribute("multiple")&&s.getAttribute("multiple").toLowerCase()!=="false"?m.push(i):m=[i],H(m,e,s)&&(n=l.newFileList(m),w.splice(f,1),p.files=l.newFileList(w),l.triggerEvent("change",p,{filebokzAction:"remove"}))}n&&n.length&&(s.files=n,l.triggerEvent("change",s))},K=(t,e)=>{t.preventDefault(),t.stopPropagation();let s=document.elementFromPoint(t.pageX,t.pageY);if(s){let n=document.getElementById(e),r=s.closest("[filebokz-id]");r&&r.classList.contains("js-enabled")?(r.id!==e&&(t.target.classList.add("is-transferring"),n.classList.add("is-transferring")),t.target.classList.remove("is-removing"),n.classList.remove("is-removing")):(t.target.classList.add("is-removing"),n.classList.add("is-removing"),t.target.classList.remove("is-transferring"),n.classList.remove("is-transferring"))}},V=(t,e,s)=>{t.target.classList.add("is-dragging");let n=Array.from(t.target.parentNode.children).indexOf(t.target);t.dataTransfer.setData("fileBoxId",e),t.dataTransfer.setData("fileIndex",n)},X=(t,e,s)=>{t.preventDefault(),t.stopPropagation(),l.removeFiles(e,s)},Z=(t,e)=>{e.classList.add("in-focus")},J=(t,e,s)=>{let n=e.querySelector(".error");n&&(n.innerHTML=""),e.classList.remove("error"),l.triggerEvent("change",s)},Q=(t,e)=>{e.classList.add("is-uploading")},_=t=>{t.preventDefault()},B=t=>{t.preventDefault(),t.stopImmediatePropagation();let e=t.dataTransfer.getData("fileBoxId");if(e){let n=document.getElementById(e).querySelector("input"),r=t.dataTransfer.getData("fileIndex");l.removeFiles(n,r)}},H=(t,e,s)=>{let n=e.dataset,f=s.hasAttribute("multiple")&&s.getAttribute("multiple").toLowerCase()!=="false"?Object.prototype.hasOwnProperty.call(n,"maxFiles")?n.maxFiles:null:1,o=n.maxFileSize,p=n.maxSize,y=n.allowedExtensions?n.allowedExtensions.split(",").map(i=>i.replace(/^(\.)/,"")):null,w=0;if(f&&t.length>f)return T(e,"maxFiles",f),!1;for(let i=0;i<t.length;i++){let m=t[i].name.split(".");if(m?m=m.pop().toLowerCase():m="[none]",w+=t[i].size,o&&t[i].size>o)return T(e,"maxFileSize",o),!1;if(p&&w>p)return T(e,"maxSize",p),!1;if(y&&!y.includes(m))return T(e,"allowedExtensions",y.join(", ")),!1}return!0};for(let t=0;t<a.length;t++)(function(e){let s=e.closest("form"),n=e.querySelector('input[type="file"]');if(!(!n||e.classList.contains("no-js")||Object.prototype.hasOwnProperty.call(e.dataset,"filebokzId"))){if(l.count++,e.dataset.filebokzId=l.count,e.classList.add("js-enabled"),c&&!e.classList.contains(c)&&e.classList.add(c),Y&&e.classList.add("is-advanced"),D&&e.classList.add("is-draggable"),e.id||(e.id="filebokz-"+l.count),e.dataset.allowedExtensions&&!n.getAttribute("accept")){let r=e.dataset.allowedExtensions.split(",").map(f=>f.replace(/^([^.])/,".$1"));n.setAttribute("accept",r.join(","))}e.addEventListener("dragover",function(r){U(r,e,n)},!1),e.addEventListener("dragenter",function(r){U(r,e,n)},!1),e.addEventListener("dragleave",function(r){G(r,e,n)},!1),e.addEventListener("drop",function(r){W(r,e,n)},!1),n.addEventListener("change",function(r){C(r,e,n)},!1),n.addEventListener("focus",function(r){Z(r,e)},!1),n.addEventListener("blur",function(r){N(r,e)},!1),s&&(e.dataset.autoSubmit&&e.dataset.autoSubmit.toLowerCase()!=="false"&&n.addEventListener("change",function(r){s.submit()},!1),s.addEventListener("reset",function(r){J(r,e,n)},!1),s.addEventListener("submit",function(r){Q(r,e)},!1)),C(new Event("change"),e,n)}})(a[t]);return window.addEventListener("dragover",function(t){_(t)},!1),window.addEventListener("drop",function(t){B(t)},!1),a};l.addFiles=(a,c)=>{let d=Array.from(a.files);d.concat(Array.from(c)),a.files=l.newFileList(d),l.triggerEvent("change",a)};l.newFileList=a=>{let c;try{c=new DataTransfer}catch{c=new ClipboardEvent("")}for(let d=0;d<a.length;d++)c.items.add(a[d]);return c.files};l.removeFiles=(a,c,d)=>{let L=Array.from(a.files);L.splice(c||0,d||1),a.files=l.newFileList(L),l.triggerEvent("change",a,{filebokzAction:"remove"})};l.triggerEvent=(a,c,d,L)=>setTimeout(function(){let A=new Event(a);for(let D in d)Object.prototype.hasOwnProperty.call(d,D)&&(A[D]=d[D]);c.dispatchEvent(A)},L||1);var $=l;function z(a,c){let d=document.getElementById(a);c?d.setAttribute("disabled","disabled"):d.removeAttribute("disabled")}$();z("submitBtn",!0);var x=document.querySelector(".filebokz");x.addEventListener("file-added",a=>{z("submitBtn",!1)});x.addEventListener("file-removed",a=>{a.target.classList.contains("has-files")||z("submitBtn",!0)});document.forms.namedItem("upload").onsubmit=()=>{z("submitBtn",!0)};
/*!
  filebokz v0.1.2 (https://github.com/kodie/filebokz)
  by Kodie Grantham (https://kodieg.com)
*/