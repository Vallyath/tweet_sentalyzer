import React from 'react';
import SearchBar from '../SearchBar/SearchBar';
import './App.css';

class App extends React.Component {
  constructor(props){
    super(props);
  }

  render(){
    return (
      <div className="Search">
        <SearchBar/>
      </div>
    )
  }
}

export default App;
