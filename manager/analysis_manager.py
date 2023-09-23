from builder.credentials_builder import LoginBuilder
from builder.api_calls_builder import CallsBuilder


class AnalysisManager:
    @staticmethod
    def operation():
        with LoginBuilder() as login:
            header = login.get_header()

        with CallsBuilder() as api:
            report_code = "ZQRnjtcqAmJT1d8k"
            query = """query($code: String){
            reportData{
                report(code:$code){
                fights(difficulty:5){
                id
                name
                fightPercentage
                startTime
                endTime
                } } } }"""
            query_2 = """query($code: String, $filterExpression: String){
            reportData{
                report(code:$code){
                events(fightIDs:[11], filterExpression:$filterExpression){
                data
                } } } }"""
            filterExpression = """type = "cast" and ability.id in (108280, 98008, 265202, 115310, 322118, 316958, 31821)"""

            data = api.make_call(header, query_2, code=report_code, filterExpression=filterExpression)
            print(data)

    operation()
