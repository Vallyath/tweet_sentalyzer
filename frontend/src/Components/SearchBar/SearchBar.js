import React from 'react';

class SearchBar extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            topic: ""
        }
    }

    handleTextChange = (event) => {
        this.setState({topic: event.target.value})
    }

    search = () => {
        const requestBody = {
            headers: {"Content-Type": "application/json"},
            method: "POST",
            body: JSON.stringify({topic: this.state.topic})
        }
        return fetch('http://localhost:5000/topic', requestBody).then(res => res.json()).then(data => console.log(data))
    }

    submitSearch = () => {
        this.search();
    }

    render(){
        return (
            <div className="SearchBar">
                <input placeholder="Enter a topic" onChange={this.handleTextChange}/>
                <button className="SearchButton" onClick={this.submitSearch}>SEARCH</button>
            </div>
        )
    }
}

export default SearchBar;
