function doLogin() {
	var m = document.getElementById('loginEmail');
	var p = document.getElementById('loginPWD');

	var ret = true;

	if ((m.value == 'Email') || (m.value.length < 5) || (m.indexOf('@') === -1)) {
		m.style.backgroundColor = "#f69e7a";
		m.value = 'Email';
		ret = false
	}
	if ((p.value == 'Password') || (p.value.length < 5)) {
		p.style.backgroundColor = "#f69e7a";
		p.value = 'Password';
		ret = false;
	}

	return ret;	
}

function doRegister() {
	var fn = document.getElementById('firstname');	
	var ln = document.getElementById('lastname');	
	var m  = document.getElementById('email');	

	var ret = true;

	if ((m.value == 'Email') || (m.value.length < 5) || (m.indexOf('@') === -1)) {
                m.style.backgroundColor = "#f69e7a";
                m.value = 'Email';
                ret = false
        }

	if ((fn.value == 'First Name') || (fn.value.length < 1)) {
                fn.style.backgroundColor = "#f69e7a";
                fn.value = 'First Name';
                ret = false;
        }

	if ((ln.value == 'Last Name') || (ln.value.length < 1)) {
                ln.style.backgroundColor = "#f69e7a";
                ln.value = 'Last Name';
                ret = false;
        }

	return ret;
}


function doSetPwd() {
	var p1 = document.getElementById('pwd1');
	var p2 = document.getElementById('pwd2');
	document.getElementById('checkMsg').style.visibility = 'hidden';

	var ret = true;
	if ((p1.value == 'Password') || (p1.value.length < 8) || (p1.value != p2.value)) {
		document.getElementById('checkMsg').style.visibility = 'visible';
		ret = false;	
	}
	
	return ret;
}
