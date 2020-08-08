import React from 'react';
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
                text: `Daily Sentiment Based on ${this.props.data["totaltweets"]} Tweets`
            },
            xAxis: {
                title: {
                    text: "Dates (mm/dd/yyyy)"
                },
                categories: this.props.data["dates"]
            },
            yAxis: {
                title: {
                    text: 'Sentiment (-1 for Most Negative/ 1 for Most Positive)'
                },
                max: 1,
                min: -1
            },
            series: [{
                data: this.props.data["sentiment"],
                name: 'Daily Sentiment'
            }]

        }
        return <HighchartsReact allowChartUpdate={options.allowChartUpdate} highcharts={Highcharts} options={options}/>
    }
}

export default SentimentGraph