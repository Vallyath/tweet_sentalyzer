import React from 'react';
import ReactDOM from 'react-dom';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';

class SentimentGraph extends React.Component{
    render(){
        const options = {
            chart: {
                type: 'line',
                height: "300",
                width: "500"
            },
            allowChartUpdate: true,
            title: {
                text: 'Sentiment Graph'
            },
            xAxis: {
                categories: this.props.data["dates"]
            },
            yAxis: {
                title: {
                    text: 'Sentiment (Positive - Negative)/Daily Sentiment'
                }
            },
            series: [{
                data: this.props.data["sentiment"]
            }]
        }
        return <HighchartsReact allowChartUpdate={options.allowChartUpdate} highcharts={Highcharts} options={options}/>
    }
}

export default SentimentGraph