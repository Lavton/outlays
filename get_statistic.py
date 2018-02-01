import timey_wimey
import sql_communicator
import config

month_sum = sql_communicator.get_total_sum_from_date(
        timey_wimey.get_timestamp_from_date(
            timey_wimey.get_begin_of_prev_month()
    )
)

summary = sql_communicator.get_summary_from_date(
        timey_wimey.get_timestamp_from_date(
            timey_wimey.get_begin_of_prev_month()
    ), 6
)

print("""
Общая сумма за прошлый месяц: {:.2f}

из них:
{}

(в топе {:.2f}% общей суммы)
	""".format(
		month_sum, 
		"\n".join(["{} - {} ({:.2f}%)".format(s[1], s[0], 100*s[0]/month_sum) for s in summary]),
		100*sum(map(lambda s: s[0], summary))/month_sum
	)
)


