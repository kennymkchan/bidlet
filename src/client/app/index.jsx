import React from 'react';
import {render} from 'react-dom';
// import BidletComponent from './hero.jsx';
import ListingsComponent from './listing.jsx';

// TODO: change to scss loader later
import style from './styles/app.css';

class App extends React.Component {
  render () {
    return (
      <div>
        <p> Home page!</p>
        <ListingsComponent />
      </div>
    )
  }
}

render(<App/>, document.getElementById('app'));
