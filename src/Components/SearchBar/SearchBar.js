import React from 'react';

class SearchBar extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            words: ""
        }
    }

    search = () => {
        fetch('http://localhost:5000/test').then(res => res.json()).then(result => {
            this.setState({words: result.data});
        })
    }

    submitSearch = (event) => {
        this.search();
    }

    render(){
        return (
            <div className="SearchBar">
                <input placeholder="Enter a topic" onChange={this.handleTermChange}/>
                <button className="SearchButton" onClick={this.submitSearch}>SEARCH</button>
                <h1>{this.state.words}</h1>
            </div>
        )
    }
}

export default SearchBar;