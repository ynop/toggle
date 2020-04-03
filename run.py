import argparse

import togglore
from togglore import utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool for toggle to calculate over/undertime.')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    parser_range = subparsers.add_parser('range', help='range help')
    parser_range.add_argument('from_date', help='startdate, e.g. 30.08.2016')
    parser_range.add_argument('to_date', help='enddate, e.g. 12.10.2016')

    parser_year = subparsers.add_parser('thisyear', help='today help')
    parser_thismonth = subparsers.add_parser('thismonth', help='month help')
    parser_week = subparsers.add_parser('thisweek', help='week help')
    parser_today = subparsers.add_parser('today', help='day help')
    parser_month = subparsers.add_parser('month', help='month help')
    parser_month.add_argument('month', help='month e.g. 08')
    parser_since = subparsers.add_parser('since', help='since help')
    parser_since.add_argument('since', help='since e.g. 2016.08.01')

    parser.add_argument(
        '--notify',
        action="store_true",
    )

    parser.add_argument(
        '--uses_notify_send',
        action="store_true",
    )

    args = parser.parse_args()

    client = togglore.Togglore()

    expected = 0
    actual = 0
    running = 0

    if args.command == 'range':
        actual, expected, running = client.diff(utils.DateRange.parse_from_iso_strings(args.from_date, args.to_date))
    elif args.command == 'thisyear':
        actual, expected, running = client.diff(utils.DateRange.this_year(), include_running=True)
    elif args.command == 'thismonth':
        actual, expected, running = client.diff(utils.DateRange.this_month(), include_running=True)
    elif args.command == 'thisweek':
        actual, expected, running = client.diff(utils.DateRange.this_week(), include_running=True)
    elif args.command == 'today':
        actual, expected, running = client.diff(utils.DateRange.today(), include_running=True)
    elif args.command == 'month':
        actual, expected, running = client.diff(utils.DateRange.month(int(args.month)))
    elif args.command == 'since':
        actual, expected, running = client.diff(utils.DateRange.since(args.since))


    difference = actual-expected
    output_result = (
        ("Hours to do: {0:.2f}h ({1:.2f} days)".format(expected, expected/client.cfg.work_hours_per_day)) + "\r\n" +
        ("Hours worked: {0:.2f}h ({1:.2f} days)".format(actual, actual/client.cfg.work_hours_per_day)) + "\r\n" +
        ("Difference: {0:.2f}h ({1:.2f} days)".format(difference, difference/client.cfg.work_hours_per_day))
    )
    print(output_result)

    print(f"Send notification when time is over: {'On' if args.notify else 'Off'}")
    print(f"Uses notify send when time is over: {'On' if args.uses_notify_send else 'Off'}")
    if args.notify and difference >= 0 and running:
        from gi import require_version
        require_version('Notify', '0.7')
        from gi.repository import Notify
        Notify.init("Toggle Notifier")
        notification=Notify.Notification.new(
            f'Time to stop working (+{difference:.2f}h)',
            ('-' * 112) + "\r\n" + output_result,
            "dialog-information"
        )
        notification.set_timeout(0) # persist
        notification.show ()

    if args.uses_notify_send and difference >= 0 and running:
        import os
        title = f'Time to stop working (+{difference:.2f}h)'
        os.system(
            "notify-send \"" + title + "\" " + " \"" +
            output_result + "\""
        )
    

