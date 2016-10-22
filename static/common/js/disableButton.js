var disable = (function()
{
	var button, form;

	function preventDoubleClick(index){
		button.setAttribute('disabled', 'true');
		form.submit();
	}

	function attach(){
		button = document.querySelector('input[type = "submit"]');
		form = document.querySelector('form');

		if(button){
			button.addEventListener('click', preventDoubleClick);				
		}
	}

	function init(){
		$(document).ready(attach);
	}

	return {
		init : init,
	};
	
})();