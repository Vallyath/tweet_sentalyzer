import React from 'react';
import SearchBar from '../SearchBar/SearchBar';
import './App.css';

class App extends React.Component {
  constructor(props){
    super(props);
  }

  render(){
    return (
      <div>
        <div className="Title">
          <h1>Twitter Sentiment Analyzer</h1>
        </div>
        <div className="Search">
          <SearchBar />
        </div>
      </div>
    )
  }
}

export default App;
