import React, {Component} from 'react';
import {
  DonutChart,
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
  'CS', 'EN', 'FR'
];
const verboseLanguageTable = [
  'Česky', 'Anglicky', 'Francouzsky'
];
const backends = [
  'Seznam', 'TBD', 'Google'
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
      targetValue: '',
      sourceDefHeader: '',
      targetDefHeader: '',
      sourceDefs: [],
      targetDefs: [],
      backend: 0,
      total: 0,
      translated: 0
    };
  }

  componentDidMount = () => {
    const refresh = () => axios.get('/api/v1/matrix')
        .then(d => this.setState({...d.data}))
        .catch(e => {});

    setInterval(refresh, 1000);
  };

  translate = cb => {
    axios.post(`/api/v1/translate?source_lang=${languageTable[this.state.source].toLowerCase()}&target_lang=${languageTable[this.state.target].toLowerCase()}&api=${backends[this.state.backend]}`,
      {
        text: this.state.entered,
      }
    ).then(cb).catch(e => {
      clearTimeout(this.state.timeout);
      this.setState({retrieval: null, timeout: null});
      alert(e);
    });
  };
  
  timeoutProc = () => {
    if (this.state.timeout != null) {
      clearTimeout(this.state.timeout);
    }
    if (this.state.entered.length < 1)
      return;
    let timeout = setTimeout(() => {
      this.setState({timeout: null, retrieval: true});
      this.translate(data => {
        const d = data.data;
        const tags = d.tags;
        const query = d.query.join(' ');
        const translations = d.translations;

        tv = translations.map(v => {
          const first = v.reverse().pop();
          const comma = first.search(',');
          if (comma > -1) {
            return first.substr(0, comma);
          } else {
            return first;
          }
        });

        this.setState({
          sourceValue: query,
          sourceDefs: tags,
          targetDefs: translations,
          targetValue: tv,
          retrieval: null
        });
      });
    }, 1500);
    this.setState({ timeout });
  };
  removeDecoration = {backgroundColor: '#fff', border: '0px'};
  langSelectors = {...this.removeDecoration, padding: 0}
  words = {display: 'inline-block', borderRadius: '0.25em', margin: '2px', padding: '2px'}

  focusWord = (w, parent, i) => {
    if (parent === 'source') {
      this.setState({sourceDefHeader: w, sourceDefs: this.state.sourceDefs[i]});
    } else {
      this.setState({targetDefHeader: w, targetDefs: this.state.targetDefs[i].join(', ')});
    }
  };

  selectBackend = e => this.state.backend != e && this.setState({backend: e});
  selectLangSource = e => this.state.target != e && this.setState({source: e});
  selectLangTarget = e => this.state.source != e && this.setState({target: e});
  swapLang = () => this.setState({source: this.state.target, target: this.state.source});
  tokenize = (str, parent) => { 
    if (str) { 
      console.log(str);
      str.split(' ').map((e, i) => <a href="#" className="link" onClick={() => this.focusWord(e, parent, i)} style={this.words} key={i}>{e}</a>) 
    }
  }

  render() {
    const spinnerProps = this.state.retrieval ? {loading: true} : {};
    return (
      <Grid>
        <div style={{position: 'absolute', 'top': 0, right: 0}}>
          Backend: <DropdownButton title={backends[this.state.backend]} pullRight id="backend">
            {languageTable.map(
              (e, i) => <MenuItem onSelect={this.selectBackend} active={i == this.state.backend} eventKey={i} key={i}>{backends[i]}</MenuItem>
            )}
          </DropdownButton>
          <DonutChart
            id="donunt-chart-1"
            size={{width: 210,height: 210}}
            data={{
              columns: [['Dotazu',this.state.total],['Obslouzeno',this.state.translated]],
              groups: [['used','available']],
              order: null
            }}
            tooltip={{contents: ""}}
            title={{type: 'max'}}
          />
        </div>
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
                        onChange={e => { this.setState({entered: e.target.value}, this.timeoutProc); }}/>
                      <InputGroup.Addon style={this.removeDecoration}>
                        <Spinner {...spinnerProps} inline size="sm" />
                      </InputGroup.Addon>
                    </InputGroup>
                  </Col>
                </FormGroup>
              </Form>
              <div>
                <Col sm={6}>
                  <center><h2>{verboseLanguageTable[this.state.source]}</h2></center>
                  <div className='content-view'>
                    {this.tokenize(this.state.sourceValue, 'source')}
                  </div>
                  {(this.state.sourceDefHeader || null) && <div><h2><b>{this.state.sourceDefHeader}</b></h2></div>}
                  {this.state.sourceDefs}
                  {this.state.sourceDefHeader.length > 0 && this.state.sourceDefs.length == 0 && <span>Bez definice</span>}
                </Col>
                <Col sm={6}>
                  <center><h2>{verboseLanguageTable[this.state.target]}</h2></center>
                  <div className='content-view'>
                    {this.tokenize(this.state.targetValue, 'target')}
                  </div>
                  {(this.state.targetDefHeader || null) && <div><h2><b>{this.state.targetDefHeader}</b></h2></div>}
                  {this.state.targetDefs}
                  {this.state.targetDefHeader.length > 0 && this.state.targetDefs.length == 0 && <span>Bez definice</span>}
                </Col>
              </div>
            </div>
          </Col>
        </Row>
      </Grid>
    );
  }
}
