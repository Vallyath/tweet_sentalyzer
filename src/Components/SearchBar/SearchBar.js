import React from 'react';
import SentimentGraph from '../SentimentGraph/SentimentGraph';
import LoadIcon from 'react-loader-spinner';
import './SearchBar.css'

class SearchBar extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            topic: "",
            data: {},
            showLoadIcon: false,
            showGraph: false
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
        return fetch('http://localhost:5000/topic', requestBody).then(res => res.json()).then(returnedData => {
            this.setState({data: returnedData});
            this.setShowLoadIcon(false);
            this.setShowGraph(true);
        })
    }

    setShowGraph = boolean => this.setState({showGraph: boolean});

    setShowLoadIcon = boolean => this.setState({showLoadIcon: boolean});

    submitSearch = () => {
        this.search();
        this.setShowLoadIcon(true);
    }

    render(){
        return (
            <div className="form-row">
                <div className="col-5 offset-3">
                    <input className="form-control" placeholder="Search for a topic! Ex: #TikTok" onChange={this.handleTextChange}/>
                </div>
                <div className="col">
                    <button className="btn btn-light" onClick={this.submitSearch}>Search</button>
                    <LoadIcon className="loading" type="TailSpin" color="white" visible={this.state.showLoadIcon} width="30" height="30"/>
                </div>
                <div className="Graphs">
                    { this.state.showGraph ? <SentimentGraph data={this.state.data}/>: null}
                    { this.state.showGraph ? <h6 className="calculation">Calculation is done by (Daily Positive Sentiment - Daily Negative Sentiment)/Total Daily Sentiment</h6>: null}
                </div>
            </div>
        )
    }
}

export default SearchBar;
