import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modified_heikinashi_fibonacci_functions import MRHATradingSystem, preprocess_codes, check_buy_signal

def run_analysis(file_path, market_type):
    end_date = datetime.now()
    codes = preprocess_codes(file_path, market_type)
    
    st.write(f"총 {market_type} 개수: {len(codes)}")
    
    buy_signal_codes = []
    progress_bar = st.progress(0)
    
    for i, code in enumerate(codes):
        if check_buy_signal(code, end_date):
            buy_signal_codes.append(code)
        progress_bar.progress((i + 1) / len(codes))
    
    st.write(f"\n현재 매수 신호가 있는 {market_type} 개수: {len(buy_signal_codes)}")
    
    if buy_signal_codes:
        for code in buy_signal_codes:
            st.write(f"매수 신호 {market_type}: {code}")
            
        for code in buy_signal_codes:
            st.write(f"\n{code}에 대한 상세 분석:")
            analyze_single_code(code, end_date)
    else:
        st.write(f"현재 매수 신호가 있는 {market_type}가 없습니다.")


def analyze_single_code(code, end_date):
    try:
        trading_system = MRHATradingSystem(code, end_date - timedelta(days=365), end_date)
        trading_system.run_analysis()
        
        results = trading_system.get_results()
        
        if "error" in results:
            st.error(results["error"])
            return

        st.write(f"총 수익률: {results['Total Return']:.2%}")
        st.write(f"연간 수익률: {results['Annualized Return']:.2%}")
        st.write(f"샤프 비율: {results['Sharpe Ratio']:.2f}")
        st.write(f"최대 낙폭: {results['Max Drawdown']:.2%}")
        st.write(f"총 거래 횟수: {results['Total Trades']}")
        
        fig = trading_system.plot_results()
        st.plotly_chart(fig)
    except ValueError as e:
        st.error(f"오류: {str(e)}")
    except Exception as e:
        st.error(f"예기치 못한 오류: 종목코드를 확인해서 다시 입력해 주세요: {str(e)}")


def main():
    st.title("Modified Ying Yang Fibonacci Signal")
    
    analysis_type = st.radio("분석 유형을 선택하세요:", ("ETF/KOSPI 리스트", "사용자 지정 코드"))
    
    if analysis_type == "ETF/KOSPI 리스트":
        market_type = st.radio("분석할 시장을 선택하세요:", ("ETF", "KOSPI"))
        
        if market_type == "ETF":
            file_path = "korea_etfs.csv"
        else:
            file_path = "kospi200_equity.csv"
        
        if st.button(f"{market_type} 분석 시작"):
            run_analysis(file_path, market_type)
    
    else:  # 사용자 지정 코드
        user_code = st.text_input("분석할 종목 코드를 입력하세요 (예: 005930.KS):")
        if st.button("사용자 지정 코드 분석 시작"):
            if user_code:
                st.write(f"{user_code}에 대한 상세 분석:")
                user_code=user_code+".KS"
                analyze_single_code(user_code, datetime.now())
            else:
                st.error("종목 코드를 입력해주세요.")

if __name__ == "__main__":
    main()