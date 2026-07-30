(function(){
  var overlay;
  function build(){
    overlay=document.createElement('div');
    overlay.className='im-overlay';
    overlay.innerHTML='<div class="im-panel" role="dialog" aria-modal="true" aria-label="Request a quote or enquiry">'
      +'<button class="im-close" type="button" aria-label="Close">&times;</button>'
      +'<span class="tag2">Get In Touch</span>'
      +'<h3>Request a Quote or Enquiry</h3>'
      +'<div class="im-sub">Tell us what you need — the more detail you share, the faster our team can respond.</div>'
      +'<div class="im-prod" id="imProd" style="display:none"></div>'
      +'<form class="inquiry-form" action="https://formsubmit.co/alwasit@alwasit.com" method="POST">'
      +'<input type="hidden" name="_cc" value="aq@alwasit.com">'
      +'<input type="hidden" name="_subject" id="imSubject" value="Website Enquiry — Al Wasit Machinery">'
      +'<input type="hidden" name="_template" value="table">'
      +'<input type="hidden" name="_captcha" value="false">'
      +'<input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">'
      +'<input type="hidden" name="Product" id="imProductField" value="">'
      +'<div class="frow"><label>Full name*<input type="text" name="Full Name" placeholder="Your name" required></label>'
      +'<label>Company<input type="text" name="Company" placeholder="Company name"></label></div>'
      +'<div class="frow"><label>Phone / WhatsApp*<input type="tel" name="Phone" placeholder="+971 ..." required></label>'
      +'<label>Email*<input type="email" name="Email" placeholder="name@company.com" required></label></div>'
      +'<div class="frow"><label>Country<input type="text" name="Country" placeholder="e.g. UAE"></label>'
      +'<label>Enquiry type*<select name="Enquiry Type" required><option value="" disabled selected>Select&hellip;</option>'
      +'<option>Buy New Equipment</option><option>Rent / Used Equipment</option><option>Spare Parts</option>'
      +'<option>Service &amp; Support</option><option>Plant Hire &amp; Transport</option><option>Other</option></select></label></div>'
      +'<div class="frow"><label>Equipment category<select name="Equipment Category"><option value="" selected>Any / not sure</option>'
      +'<option>Excavator</option><option>Wheel Loader</option><option>Backhoe Loader</option><option>Bulldozer</option>'
      +'<option>Motor Grader</option><option>Roller / Compactor</option><option>Forklift</option><option>Truck / Trailer</option>'
      +'<option>Attachment</option><option>Spare Parts</option><option>Other</option></select></label>'
      +'<label>Timeline<select name="Timeline"><option value="" selected>Select&hellip;</option>'
      +'<option>Immediate</option><option>Within 1 month</option><option>1&ndash;3 months</option><option>Just exploring</option></select></label></div>'
      +'<label class="ffull">Details*<textarea name="Message" rows="4" placeholder="Tell us the model(s), quantity, project or any specific requirement&hellip;" required></textarea></label>'
      +'<button type="submit" class="btn btn-o">Send Enquiry &rarr;</button>'
      +'<p class="inq-note">We usually respond within one business day. Your details are only used to answer your enquiry.</p>'
      +'</form></div>';
    document.body.appendChild(overlay);
    overlay.addEventListener('click',function(e){if(e.target===overlay)close();});
    overlay.querySelector('.im-close').addEventListener('click',close);
    document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
  }
  function open(product){
    if(!overlay)build();
    var prod=overlay.querySelector('#imProd'),pf=overlay.querySelector('#imProductField'),subj=overlay.querySelector('#imSubject');
    if(product){prod.style.display='block';prod.innerHTML='Enquiry about: <b>'+product+'</b>';pf.value=product;subj.value='Product Enquiry — '+product;}
    else{prod.style.display='none';pf.value='';subj.value='Website Enquiry — Al Wasit Machinery';}
    overlay.classList.add('open');document.body.style.overflow='hidden';
    var f=overlay.querySelector('input[name="Full Name"]');if(f){setTimeout(function(){f.focus();},60);}
  }
  function close(){if(overlay){overlay.classList.remove('open');document.body.style.overflow='';}}
  window.openInquiry=open;
  document.addEventListener('click',function(e){
    var b=e.target.closest('.inquire-btn');
    if(b){e.preventDefault();open(b.getAttribute('data-product')||'');}
  });
})();
