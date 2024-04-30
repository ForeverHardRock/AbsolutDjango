const identity = document.getElementById("identity");
const identityButton = document.getElementById("identity-button");
const inputContent = document.getElementById("input-content");
const passwordInputContent = document.getElementById("password-input-content");
const codeInputContent = document.getElementById("code-input-content");
const codeResetInputContent = document.getElementById("code-reset-input-content");

const emailErrorSpan = document.getElementById('emailError');
const passwordErrorSpan = document.getElementById('password-error');
const codeErrorSpan = document.getElementById('code-error');
const codeResetErrorSpan = document.getElementById('code-reset-error');

identity.addEventListener("input", (event) => {
  const inputValue = event.target.value;
  const isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inputValue);

  if (!isValidEmail && identity.value.length > 0) {
    emailErrorSpan.style.display = 'inline';
    inputContent.style.boxShadow = 'inset 0 0 0 1px #ba1a1a';
  } else {
    emailErrorSpan.style.display = 'none';
    inputContent.removeAttribute('style');
  }

  identityButton.disabled = identity.value.length === 0;
});

//document.getElementById("singin").addEventListener('submit', (event) => {
  //event.preventDefault();
  //submitIdentity();
//})

const password = document.getElementById("password");
const passwordButton = document.getElementById("plogin-button");

password.addEventListener("input", (event) => {
  const inputValue = event.target.value;
  if (inputValue.startsWith(' ')) {
    event.target.value = inputValue.trimStart();
  }

  passwordErrorSpan.style.display = 'none';
  passwordInputContent.removeAttribute('style');
  passwordButton.disabled = password.value.length <= 0;
});

const code = document.getElementById("code");
const codeButton = document.getElementById("clogin-button");

code.addEventListener("input", (event) => {
  event.target.value = event.target.value.replace(/\D/g, '');
  codeButton.disabled = code.value.length !== 4;
  codeErrorSpan.style.display = 'none';
  codeInputContent.removeAttribute('style');
});

const codeReset = document.getElementById("code-reset");
const codeResetButton = document.getElementById("clogin-reset-button");

codeReset.addEventListener("input", (event) => {
  event.target.value = event.target.value.replace(/\D/g, '');
  codeResetButton.disabled = codeReset.value.length !== 4;
  codeResetErrorSpan.style.display = 'none';
  codeResetInputContent.removeAttribute('style');
});

let loginMethod = '';
const backButton = document.getElementById('return-btn');
let inner;
let passwordType = 'password'

const submitIdentity = () => {
  identityButton.setAttribute('class', 'button-loading');
  identityButton.innerHTML = '';
  const data = new FormData();
  data.append("identity", identity.value);

  const response = fetch("/signin", {
    method: "POST",
    body: data, // body data type must match "Content-Type" header
  }).then(async result => {
    const json = (await result.json())
    if (result.ok) {
      backButton.setAttribute("style", "display: flex");
      code.value = '';
      password.value = '';

      if (json["loginMethod"] === "PASSWORD") {
        document.getElementById("identity-form").setAttribute("style", "display: none");
        document.getElementById("password-form").setAttribute("style", "display: block");

        document.getElementById("plogin").addEventListener('submit', (event) => {
          event.preventDefault();
          submitPasswordLogin();
        })
      }
      if (json["loginMethod"] === "EMAIL_CODE") {
        document.getElementById("identity-form").setAttribute("style", "display: none");
        document.getElementById("code-form").setAttribute("style", "display: block");
        loginMethod = json["loginMethod"];

        this.timer();

        document.getElementById("clogin").addEventListener('submit', (event) => {
          event.preventDefault();
          submitCodeLogin();
        })
      }
    } else {
      identityButton.innerHTML = 'Продолжить';
      identityButton.removeAttribute('class', 'button-loading');
    }
  });
}

const submitPasswordLogin = () => {
  passwordButton.setAttribute('class', 'button-loading');
  passwordButton.innerHTML = '';
  passwordErrorSpan.style.display = 'none';
  passwordInputContent.removeAttribute('style');

  if (password.value.endsWith(' ')) {
    password.value = password.value.trimEnd();
  }

  const data = new FormData();
  data.append("identity", identity.value);
  data.append("secret", password.value);
  data.append("loginMethod", "PASSWORD");
  const response = fetch("/login", {
    method: "POST",
    body: data, // body data type must match "Content-Type" header
  }).then(async result => {
    if (result.redirected) {
      window.location.replace(result.url);
    } else {
      if (result.status === 401) {
        passwordErrorSpan.style.display = 'inline';
        passwordInputContent.style.boxShadow = 'inset 0 0 0 1px #ba1a1a';
        passwordButton.innerHTML = 'Продолжить';
        passwordButton.removeAttribute('class', 'button-loading');
      }
    }
  });
}

const submitCodeLogin = () => {
  codeButton.setAttribute('class', 'button-loading');
  codeButton.innerHTML = '';
  codeErrorSpan.style.display = 'none';
  codeInputContent.removeAttribute('style');

  const data = new FormData();
  data.append("identity", identity.value);
  data.append("secret", code.value);
  data.append("loginMethod ", loginMethod);
  const response = fetch("/login", {
    method: "POST",
    body: data, // body data type must match "Content-Type" header
  }).then(async result => {
    if (result.redirected) {
      window.location.replace(result.url);
    } else {
      if (result.status === 401) {
        codeErrorSpan.style.display = 'inline';
        codeInputContent.style.boxShadow = 'inset 0 0 0 1px #ba1a1a';
        codeButton.innerHTML = 'Продолжить';
        codeButton.removeAttribute('class', 'button-loading');
      }
    }
  });
}

const toResetPass = () => {
  const data = new FormData();
  data.append("identity", identity.value);

  const response = fetch("/password/request", {
    method: "POST",
    body: data, // body data type must match "Content-Type" header
  }).then(async result => {
    document.getElementById("password-form").setAttribute("style", "display: none");
    document.getElementById("code-reset-form").setAttribute("style", "display: block");

    this.timerForReset();

    document.getElementById("reset").addEventListener('submit', (event) => {
      event.preventDefault();
      submitCodeResetLogin();
    })
  })
}

const submitCodeResetLogin = () => {
  codeResetButton.setAttribute('class', 'button-loading');
  codeResetButton.innerHTML = '';
  codeResetErrorSpan.style.display = 'none';
  codeResetInputContent.removeAttribute('style');

  const data = new FormData();
  data.append("identity", identity.value);
  data.append("code", codeReset.value);

  const response = fetch("/password/reset", {
    method: "POST",
    body: data, // body data type must match "Content-Type" header
  }).then(async result => {
    if (result.ok) {
      document.getElementById("reset-form").setAttribute("style", "display: block");
      document.getElementById("code-reset-form").setAttribute("style", "display: none");
    } else {
      codeResetErrorSpan.style.display = 'inline';
      codeResetInputContent.style.boxShadow = 'inset 0 0 0 1px #ba1a1a';
      codeResetButton.innerHTML = 'Продолжить';
      codeResetButton.removeAttribute('class', 'button-loading');
    }
  });
}

const sendCode = () => {
  document.getElementById("send-button").disabled = true;
  const data = new FormData();
  data.append("identity", identity.value);
  const response = fetch("/signin", {
    method: "POST",
    body: data, // body data type must match "Content-Type" header
  }).then(async _ => {
    this.timer();
  });
}

const sendResetCode = () => {
  document.getElementById("send-reset-button").disabled = true;
  const data = new FormData();
  data.append("identity", identity.value);

  const response = fetch("/password/reset", {
    method: "POST",
    body: data, // body data type must match "Content-Type" header
  }).then(async _ => {
    this.timerForReset();
  });
}

newTimerView = (time)=> {
  if (!time) return '';
  const minutes = Math.floor(time / 60);
  const seconds = time % 60;
  const paddedMinutes = minutes.toString().padStart(2, '0');
  const paddedSeconds = seconds.toString().padStart(2, '0');
  return ` через ${paddedMinutes}:${paddedSeconds}`;
}

timer = () => {
  let timer = 60;

  inner = setInterval(() => {
    if (timer > 0) {
      document.getElementById("send-button").innerHTML = 'Отправить код еще раз' + this.newTimerView(timer);
      timer--;
    } else {
      document.getElementById("send-button").innerHTML = 'Отправить код еще раз';
      document.getElementById("send-button").disabled = false;
      clearInterval(inner);
    }
  }, 1000)
}

timerForReset = () => {
  let timer = 60;

  inner = setInterval(() => {
    if (timer > 0) {
      document.getElementById("send-reset-button").innerHTML = 'Отправить код еще раз' + this.newTimerView(timer);
      timer--;
    } else {
      document.getElementById("send-reset-button").innerHTML = 'Отправить код еще раз';
      document.getElementById("send-reset-button").disabled = false;
      clearInterval(inner);
    }
  }, 1000)
}

const back = () => {
  backButton.setAttribute("style", "display: none");

  identityButton.removeAttribute('class', 'button-loading');
  identityButton.innerHTML = 'Продолжить';
  passwordButton.removeAttribute('class', 'button-loading');
  passwordButton.innerHTML = 'Продолжить';
  codeButton.removeAttribute('class', 'button-loading');
  codeButton.innerHTML = 'Продолжить';
  codeResetButton.removeAttribute('class', 'button-loading');
  codeResetButton.innerHTML = 'Продолжить';

  document.getElementById("identity-form").setAttribute("style", "display: block");
  document.getElementById("password-form").setAttribute("style", "display: none");
  document.getElementById("code-form").setAttribute("style", "display: none");
  document.getElementById("reset-form").setAttribute("style", "display: none");
  document.getElementById("code-reset-form").setAttribute("style", "display: none");

  document.getElementById("send-button").disabled = true;
  document.getElementById("send-button").innerHTML = 'Отправить код еще раз';
  document.getElementById("send-reset-button").disabled = true;
  document.getElementById("send-reset-button").innerHTML = 'Отправить код еще раз';

  emailErrorSpan.style.display = 'none';
  passwordErrorSpan.style.display = 'none';
  codeErrorSpan.style.display = 'none';
  codeResetErrorSpan.style.display = 'none';
  inputContent.removeAttribute('style');
  passwordInputContent.removeAttribute('style');
  codeInputContent.removeAttribute('style');
  codeResetInputContent.removeAttribute('style');

  clearInterval(inner);
}

changePasswordType = () => {
  passwordType = passwordType === 'text' ? 'password' : 'text' ;
  password.setAttribute('type', passwordType);
  document.getElementById('password-icon').setAttribute('src', passwordType === 'text' ?  'visibility.svg' : 'visibility-off.svg')
}