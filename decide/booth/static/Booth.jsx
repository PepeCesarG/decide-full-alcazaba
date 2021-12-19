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

  decideEncrypt() {
    var bigmsg = BigInt.fromJSONObject(this.state.selected.toString());
    var cipher = ElGamal.encrypt(this.state.bigpk, bigmsg);
    return cipher;
  }

  LoginForm(props) {
    return (
      <div id="loginForm">
        <form onSubmit={this.onSubmitLogin}>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            required
            autoComplete="username"
            onChange={this.onUsernameChange}
          />
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            required
            onChange={this.onPasswordChange}
          />
          <button type="submit">Login</button>
        </form>
      </div>
    );
  }

  render() {
    return (
      <>
        {this.Navbar()}
        <div id="voting">
          <h1>
            {this.state.voting.id} - {this.state.voting.name}
          </h1>

          {this.state.alertShow && (
            <div className={"alert " + this.state.alertLvl}>
              <button type="button" onClick={this.onClickAlert}>
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

