import React from 'react';
import {render} from 'react-dom';
import BidletComponent from './hero.jsx';

// TODO: change to scss loader later
import style from './styles/app.css';

class App extends React.Component {
  render () {
    return (
      <div>
        <p> Hello React!</p>
        <BidletComponent />
      </div>
    )
  }
}

render(<App/>, document.getElementById('app'));
