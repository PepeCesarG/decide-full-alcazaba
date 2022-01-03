class Booth extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      keybits: 256,
      voting: this.props.voting,
      selected: "",
      signup: true,
      alertShow: false,
      alertMsg: "",
      alertLvl: "info",
      token: null,
      user: null,
      form: {
        username: "",
        password: "",
      },
      bigpk: {
        p: BigInt.fromJSONObject(this.props.voting.pub_key.p.toString()),
        g: BigInt.fromJSONObject(this.props.voting.pub_key.g.toString()),
        y: BigInt.fromJSONObject(this.props.voting.pub_key.y.toString()),
      },
    };
    this.onSelect = this.onSelect.bind(this);
    this.onUsernameChange = this.onUsernameChange.bind(this);
    this.onPasswordChange = this.onPasswordChange.bind(this);
    this.decideSend = this.decideSend.bind(this);
    this.onSubmitLogin = this.onSubmitLogin.bind(this);
    this.onClickAlert = this.onClickAlert.bind(this);
    this.decideLogout = this.decideLogout.bind(this);
  }

  componentDidMount() {
    this.init();
    ElGamal.BITS = this.state.keybits;
  }

  init() {
    var cookies = document.cookie.split("; ");
    cookies.forEach((c) => {
      var cs = c.split("=");
      if (cs[0] == "decide" && cs[1]) {
        this.setState({ token: cs[1] }, () => this.getUser());
      }
    });
  }

  async postData(url, data) {
    // Default options are marked with *
    var fdata = {
      body: JSON.stringify(data),
      headers: {
        "content-type": "application/json",
      },
      method: "POST",
    };

    if (this.state.token) {
      fdata.headers["Authorization"] = "Token " + this.state.token;
    }

    return fetch(url, fdata).then((response) => {
      if (response.status === 200) {
        return response.json();
      } else {
        return Promise.reject(response.statusText);
      }
    });
  }

  onSubmitLogin(e) {
    e.preventDefault();
    this.postData("/gateway/authentication/login/", this.state.form)
      .then((data) => {
        document.cookie = "decide=" + data.token + ";";
        this.setState({ token: data.token }, () => this.getUser());
      })
      .catch((error) => {
        this.showAlert("danger", "Error: " + error);
      });
  }

  decideLogout(e) {
    e.preventDefault();
    var data = { token: this.state.token };
    this.postData("/gateway/authentication/logout/", data);
    this.setState({ token: null });
    this.setState({ user: null });
    document.cookie = "decide=;";
    this.setState({ signup: true });
  }

  getUser(e) {
    var data = { token: this.state.token };
    this.postData("/gateway/authentication/getuser/", data)
      .then((data) => {
        this.setState({ user: data });
        this.setState({ signup: false });
      })
      .catch((error) => {
        this.showAlert("danger", "Error: " + error);
      });
  }

  decideEncrypt() {
    var bigmsg = BigInt.fromJSONObject(this.state.selected.toString());
    var cipher = ElGamal.encrypt(this.state.bigpk, bigmsg);
    return cipher;
  }

  decideSend(e) {
    e.preventDefault();
    var v = this.decideEncrypt();
    var data = {
      vote: { a: v.alpha.toString(), b: v.beta.toString() },
      voting: this.state.voting.id,
      voter: this.state.user.id,
      token: this.state.token,
    };
    this.postData("/gateway/store/", data)
      .then((data) => {
        this.showAlert("success", "Conglatulations. Your vote has been sent");
      })
      .catch((error) => {
        this.showAlert("danger", "Error: " + error);
      });
  }

  showAlert(lvl, msg) {
    this.setState({ alertLvl: lvl });
    this.setState({ alertMsg: msg });
    this.setState({ alertShow: true });
  }

  onSelect(e) {
    this.setState({ selected: e.target.value });
  }

  onUsernameChange(e) {
    this.setState((state) => ({
      form: { username: e.target.value, password: state.form.password },
    }));
  }

  onPasswordChange(e) {
    this.setState((state) => ({
      form: { username: state.form.username, password: e.target.value },
    }));
  }

  onClickAlert(e) {
    this.setState({ alertShow: false });
  }

  Navbar(props) {
    return (
      
      <div className="navbar" class="navbar-div">
        <h1 class="decide-h1">Decide</h1>
        {!this.state.signup && (
          <a href="#" onClick={this.decideLogout} class="logout">
            logout
          </a>
        )}
      </div>
      
    );
  }

  LoginForm(props) {
    return (
      <div id="loginForm" class="login-div">
        <form onSubmit={this.onSubmitLogin}>
          <label htmlFor="username" class="username-label">Username</label>
          <input
            id="username"
            type="text"
            required
            autoComplete="username"
            onChange={this.onUsernameChange}
            class ="username-input"
          />
          <label htmlFor="password" class="password-label">Password</label>
          <input
            id="password"
            type="password"
            required
            onChange={this.onPasswordChange}
            class="password-input"
          />
          <button type="submit" class="button-submit">Login</button>
        </form>
      </div>
    );
  }

  VotingForm(props) {
    return (
      <div id="votingForm" class="votingform-div">
        <h2 class="pregunta-h2">{this.state.voting.question.desc}</h2>
        <form>
          {this.state.voting.question.options.map((opt) => (
            <div className="radio" key={opt.number} class ="radio-div">
              <label class="opt-label" class="opt-label">
                <input
                  type="radio"
                  id={"q" + opt.number}
                  name={this.state.voting.question}
                  value={opt.number}
                  onChange={this.onSelect}
                />
                {opt.option}
              </label>
            </div>
          ))}
        </form>
        <button type="button" onClick={this.decideSend} class="button-submit">
          Vote
        </button>
      </div>
    );
  }

  render() {
    return (
      <>
        {this.Navbar()}
        <div id="voting" class="voting-div">
          <h1 class="titulo-h1">
            {this.state.voting.id} - {this.state.voting.name}
          </h1>

          {this.state.alertShow && (
            <div className={"alert " + this.state.alertLvl} class="alert-div">
              <button type="button" onClick={this.onClickAlert} class="button-alert">
                x
              </button>
              {this.state.alertMsg}
            </div>
          )}

          {this.state.signup ? this.LoginForm() : this.VotingForm()}
        </div>
      </>
    );
  }
}