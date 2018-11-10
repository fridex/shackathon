import React, {Component} from 'react';
import {
  Spinner,
  Grid,
  Row,
  Col,
  Form,
  FormGroup,
  FormControl,
  ControlLabel,
  InputGroup,
  DropdownButton,
  MenuItem,
  Icon,
  Button
} from 'patternfly-react';
import axios from 'axios';
import axiosRetry from 'axios-retry';

axiosRetry(axios, {
  retries: Number.MAX_SAFE_INTEGER,
  retryDelay: () => 10000,
});

const languageTable = [
  'CZ', 'EN', 'FR'
];

export default class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      entered: '',
      source: 0,
      target: 1,
      timeout: null,
      retrieval: null,
      sourceValue: '',
      targetValue: 'this is an example',
      sourceDefHeader: '',
      targetDefHeader: '',
      sourceDefs: ['First meaning', 'Second meaning', 'Third meaning'],
      targetDefs: []
    };
  }

  timeoutProc = () => {
    if (this.state.timeout != null) {
      clearTimeout(this.state.timeout);
    }
    let timeout = setTimeout(() => {
      this.setState({timeout: null});
      console.log(`Looking up ${this.state.entered}`);
      if (this.state.entered.length > 0) {
        let retrieval = setTimeout(() => {
          this.setState({retrieval: null});
          this.setState({sourceValue: this.state.entered});
          console.log(` -- results for: ${this.state.entered}`);
        }, 3000);
        this.setState({ retrieval });
      }
    }, 750);
    this.setState({ timeout });
  };
  removeDecoration = {backgroundColor: 'auto', border: '0px'};
  langSelectors = {...this.removeDecoration, padding: 0}
  words = {display: 'inline-block', borderRadius: '0.25em', margin: '2px', padding: '2px'}

  focusWord = (w, parent) => {
    if (parent === 'source') {
      this.setState({sourceDefHeader: w});
    } else {
      this.setState({targetDefHeader: w});
    }
  };
  selectLangSource = e => this.state.target != e && this.setState({source: e});
  selectLangTarget = e => this.state.source != e && this.setState({target: e});
  swapLang = () => this.setState({source: this.state.target, target: this.state.source});
  tokenize = (str, parent) => str.split(' ').map((e, i) => <a href="#" className="link" onClick={() => this.focusWord(e, parent)} style={this.words} key={i}>{e}</a>)

  render() {
    const spinnerProps = this.state.retrieval ? {loading: true} : {};
    return (
      <Grid>
        <Row>
          <Col md={12}>
            <center>
              <h1>Jabberwocky</h1>
            </center>
            <div className="form-wrapper">
              <Form>
                <FormGroup controlId="name" disabled={false}>
                  <Col componentClass={ControlLabel} sm={3} />
                  <Col sm={9}>
                    <InputGroup style={{width: '80%'}}>
                      <InputGroup.Addon>
                        Zadejte výraz
                      </InputGroup.Addon>
                      <InputGroup.Addon style={this.langSelectors}>
                        <DropdownButton title={languageTable[this.state.source]} id="sourceLang">
                          {languageTable.map(
                            (e, i) => <MenuItem onSelect={this.selectLangSource} active={i == this.state.source} eventKey={i} key={i}>{languageTable[i]}</MenuItem>
                          )}
                        </DropdownButton>
                      </InputGroup.Addon>
                      <InputGroup.Addon style={this.langSelectors}>
                        <Button onClick={this.swapLang}>
                          <Icon name="exchange" />
                        </Button>
                      </InputGroup.Addon>
                      <InputGroup.Addon style={this.langSelectors}>
                        <DropdownButton title={languageTable[this.state.target]} id="targetLang">
                          {languageTable.map(
                            (e, i) => <MenuItem onSelect={this.selectLangTarget} active={i == this.state.target} eventKey={i} key={i}>{languageTable[i]}</MenuItem>
                          )}
                        </DropdownButton>
                      </InputGroup.Addon>
                      <FormControl type="text" disabled={this.state.retrieval != null} 
                        value={this.state.entered} 
                        onChange={e => { this.setState({entered: e.target.value}); this.timeoutProc(); }}/>
                      <InputGroup.Addon style={this.removeDecoration}>
                        <Spinner {...spinnerProps} inline size="sm" />
                      </InputGroup.Addon>
                    </InputGroup>
                  </Col>
                </FormGroup>
              </Form>
              <div>
                <Col sm={6}>
                  <center><h2>Source</h2></center>
                  <div className='content-view'>
                    {this.tokenize(this.state.sourceValue, 'source')}
                  </div>
                  {(this.state.sourceDefHeader || null) && <div><h2><b>{this.state.sourceDefHeader}</b></h2></div>}
                  {this.state.sourceDefs.map(
                    (e, i) => <p key={i}>{e}</p>
                  )}
                </Col>
                <Col sm={6}>
                  <center><h2>Target</h2></center>
                  <div className='content-view'>
                    {this.tokenize(this.state.targetValue, 'target')}
                  </div>
                  {(this.state.targetDefHeader || null) && <div><h2><b>{this.state.targetDefHeader}</b></h2></div>}
                </Col>
              </div>
            </div>
          </Col>
        </Row>
      </Grid>
    );
  }
}
